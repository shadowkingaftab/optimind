#!/usr/bin/env python
"""Run external validation on a frozen checkpoint and thresholds."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from eyedx_ml.data.loaders import MultiLabelDataset, build_dataloader
from eyedx_ml.errors import NotConfiguredError
from eyedx_ml.evaluation import run_external_validation, write_report
from eyedx_ml.models.model_config import load_model_config
from eyedx_ml.models.model_factory import build_model
from eyedx_ml.training.checkpoint_manager import load_checkpoint
from eyedx_ml.utils.config_loader import ConfigError, load_config
from eyedx_ml.utils.logging import get_logger

logger = get_logger("eyedx_ml.external_validate")


def _require(path: str | None, label: str) -> str:
    if not path or not Path(path).is_file():
        raise NotConfiguredError(f"{label} not found ({path}) (INPUT_REQUIRED)")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
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
        split_csv = _require(data_cfg.get("manifest"), "external manifest") if False else _require(data_cfg.get("manifest"), "manifest")  # keep simple
        image_root = _require(data_cfg.get("image_root"), "image_root")
        checkpoint = _require(model_cfg.get("checkpoint"), "checkpoint")
        model_config_path = _require(model_cfg.get("config"), "model config")
    except NotConfiguredError as exc:
        logger.error("%s", exc)
        return 3

    # use the configured external manifest if present
    ext_manifest = data_cfg.get("manifest")
    if ext_manifest and Path(ext_manifest).is_file():
        manifest_path = ext_manifest

    from eyedx_ml.data.ingestion import read_manifest

    model_config = load_model_config(model_config_path)
    labels = model_config.load_approved_labels()
    records = read_manifest(manifest_path)
    ds = MultiLabelDataset(records, image_root=image_root, label_order=labels)
    loader = build_dataloader(ds, batch_size=32, shuffle=False)

    model = build_model(model_config)
    load_checkpoint(checkpoint, model=model, map_location="cpu")

    import numpy as np
    import torch

    y_true, y_score = [], []
    for batch in loader:
        inputs, targets = batch
        with torch.no_grad():
            logits = model(inputs)
            if isinstance(logits, dict):
                raise NotConfiguredError("single-output model")
            y_true.append(targets.cpu().numpy())
            y_score.append(torch.sigmoid(logits).cpu().numpy())
    y_true, y_score = np.concatenate(y_true), np.concatenate(y_score)

    report = run_external_validation(
        y_true,
        y_score,
        labels=labels,
        thresholds=config.get("thresholds") or {},
        model_id=model_cfg.get("model_id"),
        model_version=model_cfg.get("model_version"),
        dataset=config.get("name"),
        bootstrap=bool((config.get("bootstrap") or {}).get("enabled", True)),
    )
    out = config.get("output", {}).get("report") or "ml/outputs/reports/external-evaluation.json"
    path = write_report(report, out)
    logger.info("external evaluation report written to %s", path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
