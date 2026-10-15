#!/usr/bin/env python
"""Evaluate a checkpoint on a dataset split.

Produces an evaluation report (JSON) using approved thresholds or
threshold-free metrics when thresholds are absent. Requires an approved label
map and must not tune on external data.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from eyedx_ml.data.loaders import MultiLabelDataset, build_dataloader
from eyedx_ml.errors import LabelUnavailableError, NotConfiguredError
from eyedx_ml.evaluation import Evaluator, build_evaluation_report, write_report
from eyedx_ml.models.model_config import load_model_config
from eyedx_ml.models.model_factory import build_model
from eyedx_ml.training.checkpoint_manager import load_checkpoint
from eyedx_ml.utils.config_loader import ConfigError, load_config
from eyedx_ml.utils.logging import get_logger

logger = get_logger("eyedx_ml.evaluate")


def _require(path: str | None, label: str) -> str:
    if not path or not Path(path).is_file():
        raise NotConfiguredError(f"{label} not found ({path}) (INPUT_REQUIRED)")
    return path


def _load_records(split_csv: str, all_records):
    with Path(split_csv).open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        ids = {row["record_id"] for row in reader}
    by_id = {r.record_id: r for r in all_records}
    return [by_id[rid] for rid in ids if rid in by_id]


def _collect_preds(model, loader, labels):
    import numpy as np
    import torch

    y_true = []
    y_score = []
    for batch in loader:
        inputs, targets = batch
        with torch.no_grad():
            logits = model(inputs)
            if isinstance(logits, dict):
                raise NotConfiguredError("evaluator expects a single-output model")
            probs = torch.sigmoid(logits).cpu().numpy()
        y_true.append(targets.cpu().numpy())
        y_score.append(probs)
    return np.concatenate(y_true), np.concatenate(y_score)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=False)
    args = parser.parse_args(argv)

    try:
        config = load_config(args.config)
    except ConfigError as exc:
        logger.error("%s", exc)
        return 2

    data_cfg = config.get("data", {}) or {}
    model_cfg = config.get("model", {}) or {}
    try:
        manifest_path = _require(data_cfg.get("manifest"), "manifest")
        splits_dir = data_cfg.get("splits_dir") or ""
        split = data_cfg.get("split", "test")
        split_csv = _require(str(Path(splits_dir) / f"{split}.csv"), "split csv")
        image_root = _require(data_cfg.get("image_root"), "image_root")
        checkpoint = _require(model_cfg.get("checkpoint"), "checkpoint")
        model_config_path = _require(model_cfg.get("config"), "model config")
    except NotConfiguredError as exc:
        logger.error("%s", exc)
        return 3

    from eyedx_ml.data.ingestion import read_manifest

    try:
        model_config = load_model_config(model_config_path)
        labels = model_config.load_approved_labels()
    except LabelUnavailableError as exc:
        logger.error("approved labels unavailable: %s", exc)
        return 3

    records = read_manifest(manifest_path)
    eval_records = _load_records(split_csv, records)
    ds = MultiLabelDataset(eval_records, image_root=image_root, label_order=labels)
    loader = build_dataloader(ds, batch_size=int(data_cfg.get("batch_size", 32)), shuffle=False)

    model = build_model(model_config)
    load_checkpoint(checkpoint, model=model, map_location="cpu")

    y_true, y_score = _collect_preds(model, loader, labels)
    evaluator = Evaluator(
        labels,
        thresholds=dict(config.get("thresholds") or {}),
        bootstrap=bool((config.get("bootstrap") or {}).get("enabled", False)),
        n_resamples=int((config.get("bootstrap") or {}).get("n_resamples", 1000)),
        confidence_level=float((config.get("bootstrap") or {}).get("confidence_level", 0.95)),
        seed=int((config.get("bootstrap") or {}).get("seed", 42)),
    )
    metrics = evaluator.evaluate(y_true, y_score)
    report = build_evaluation_report(
        metrics,
        split=split,
        model_id=model_cfg.get("model_id"),
        model_version=model_cfg.get("model_version"),
        dataset=config.get("name"),
    )
    out = config.get("output", {}).get("report") or args.output
    if not out:
        out = f"ml/outputs/reports/{split}-evaluation.json"
    path = write_report(report, out)
    logger.info("evaluation report written to %s", path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
