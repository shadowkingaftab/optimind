#!/usr/bin/env python
"""Train a screening model from a training config.

Wires the training config to :class:`eyedx_ml.training.Trainer`. Requires an
approved label map, a canonical manifest, split files and an image directory.
The script never downloads data, never fabricates labels or metrics, and refuses
to run when required inputs (labels, manifest, splits) are missing.

Usage:
    python ml/scripts/train.py --config ml/configs/training/baseline.yaml
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from eyedx_ml.data.ingestion import DatasetError, read_manifest
from eyedx_ml.data.loaders import MultiLabelDataset, build_dataloader
from eyedx_ml.errors import (
    ArtifactUnavailableError,
    LabelUnavailableError,
    NotConfiguredError,
)
from eyedx_ml.models.losses import weighted_bce
from eyedx_ml.models.model_config import load_model_config
from eyedx_ml.training import Trainer
from eyedx_ml.utils.config_loader import ConfigError, load_config
from eyedx_ml.utils.logging import get_logger

logger = get_logger("eyedx_ml.train")


def _require_file(path: str | None, label: str) -> str:
    if not path or not Path(path).is_file():
        raise NotConfiguredError(
            f"{label} not found ({path}); provide it before training (INPUT_REQUIRED)"
        )
    return path


def _records_for_split(split_csv: str, records: list) -> list:
    import csv

    with Path(split_csv).open("r", encoding="utf-8", newline="") as handle:
        ids = {row["record_id"] for row in csv.DictReader(handle)}
    by_id = {r.record_id: r for r in records}
    return [by_id[rid] for rid in ids if rid in by_id]


def _build_criterion(model_config, train_dataset):
    loss_cfg = getattr(model_config, "loss", {}) or {}
    name = loss_cfg.get("name", "weighted_bce")
    if name == "weighted_bce":
        positives = train_dataset.positive_counts()
        total = len(train_dataset.records)
        pos_weight = [
            ((total - p) / p) if p > 0 else 1.0 for p in positives
        ]
        return lambda logits, targets: weighted_bce(logits, targets, pos_weight=pos_weight)
    raise NotConfiguredError(f"unsupported loss for training: {name}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, help="training config YAML")
    parser.add_argument("--model-id", default=None)
    parser.add_argument("--model-version", default=None)
    args = parser.parse_args(argv)

    try:
        config = load_config(args.config)
    except ConfigError as exc:
        logger.error("configuration error: %s", exc)
        return 2

    data_cfg = config.get("data", {}) or {}
    try:
        manifest_path = _require_file(data_cfg.get("manifest"), "manifest")
        splits_dir = data_cfg.get("splits_dir")
        if not splits_dir:
            raise NotConfiguredError("data.splits_dir is required (INPUT_REQUIRED)")
        image_root = _require_file(data_cfg.get("image_root"), "image_root")
    except NotConfiguredError as exc:
        logger.error("%s", exc)
        return 3

    # Fail early if the approved label map is missing.
    model_cfg_path = (config.get("model") or {}).get("config")
    if not model_cfg_path:
        logger.error("model.config is required in the training config")
        return 2
    try:
        model_config = load_model_config(model_cfg_path)
        labels = model_config.load_approved_labels()
    except LabelUnavailableError as exc:
        logger.error("approved labels unavailable: %s", exc)
        return 3

    from eyedx_ml.utils.config_loader import load_config as _load
    from eyedx_ml.data.ingestion import load_label_map  # noqa: F401  (validates map)

    try:
        records = read_manifest(manifest_path)
    except DatasetError as exc:
        logger.error("could not read manifest: %s", exc)
        return 4
    if not records:
        logger.error("manifest contains no records")
        return 4

    train_csv = Path(splits_dir) / f"{data_cfg.get('train_split', 'train')}.csv"
    val_csv = Path(splits_dir) / f"{data_cfg.get('validation_split', 'validation')}.csv"
    try:
        train_csv = _require_file(str(train_csv), "train split")
        val_csv = _require_file(str(val_csv), "validation split")
    except NotConfiguredError as exc:
        logger.error("%s", exc)
        return 3

    train_records = _records_for_split(train_csv, records)
    val_records = _records_for_split(val_csv, records)
    if not train_records or not val_records:
        logger.error("train or validation split has no matching records")
        return 4

    train_ds = MultiLabelDataset(train_records, image_root=image_root, label_order=labels)
    val_ds = MultiLabelDataset(val_records, image_root=image_root, label_order=labels)

    batch_size = int((config.get("training") or {}).get("batch_size", 16))
    seed = int((config.get("reproducibility") or {}).get("seed", 42))
    train_loader = build_dataloader(
        train_ds, batch_size=batch_size, shuffle=True, num_workers=int(data_cfg.get("num_workers", 0)), seed=seed
    )
    val_loader = build_dataloader(
        val_ds, batch_size=batch_size, shuffle=False, num_workers=int(data_cfg.get("num_workers", 0))
    )

    trainer = Trainer(config)
    try:
        trainer.setup(model_id=args.model_id, model_version=args.model_version)
    except (LabelUnavailableError, ArtifactUnavailableError, NotConfiguredError) as exc:
        logger.error("setup failed: %s", exc)
        return 5

    criterion = _build_criterion(model_config, train_ds)
    history = trainer.fit(train_loader, val_loader, criterion)
    trainer.close()

    logger.info("training finished; %d epoch(s) recorded", len(history))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
