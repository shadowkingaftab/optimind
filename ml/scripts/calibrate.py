#!/usr/bin/env python
"""Calibrate a model using temperature scaling or isotonic regression.

Fits a calibrator on the validation split and writes a calibration report and
calibration artifact. Calibration must be done on validation data only; no
threshold tuning is performed by this script.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from eyedx_ml.calibration import (
    IsotonicCalibrator,
    TemperatureScaler,
    build_calibration_report,
)
from eyedx_ml.data.loaders import MultiLabelDataset, build_dataloader
from eyedx_ml.errors import NotConfiguredError
from eyedx_ml.models.model_config import load_model_config
from eyedx_ml.models.model_factory import build_model
from eyedx_ml.training.checkpoint_manager import load_checkpoint
from eyedx_ml.utils.config_loader import ConfigError, load_config
from eyedx_ml.utils.logging import get_logger

logger = get_logger("eyedx_ml.calibrate")


def _require(path: str | None, label: str) -> str:
    if not path or not Path(path).is_file():
        raise NotConfiguredError(f"{label} not found ({path}) (INPUT_REQUIRED)")
    return path


def _collect(model, loader):
    import numpy as np
    import torch

    y_true, y_score = [], []
    for batch in loader:
        inputs, targets = batch
        with torch.no_grad():
            logits = model(inputs)
            if isinstance(logits, dict):
                raise NotConfiguredError("expects single-output model")
            probs = torch.sigmoid(logits).cpu().numpy()
        y_true.append(targets.cpu().numpy())
        y_score.append(probs)
    return np.concatenate(y_true), np.concatenate(y_score)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--method", default="temperature", choices=["temperature", "isotonic"])
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
        splits_dir = data_cfg.get("splits_dir", "")
        val_csv = _require(str(Path(splits_dir) / "validation.csv"), "validation.csv")
        image_root = _require(data_cfg.get("image_root"), "image_root")
        checkpoint = _require(model_cfg.get("checkpoint"), "checkpoint")
        model_config_path = _require(model_cfg.get("config"), "model config")
    except NotConfiguredError as exc:
        logger.error("%s", exc)
        return 3

    from eyedx_ml.data.ingestion import read_manifest

    model_config = load_model_config(model_config_path)
    labels = model_config.load_approved_labels()
    records = read_manifest(manifest_path)
    # collect validation records
    with Path(val_csv).open("r", encoding="utf-8", newline="") as handle:
        ids = {r["record_id"] for r in csv.DictReader(handle)}
    by_id = {r.record_id: r for r in records}
    val_records = [by_id[rid] for rid in ids if rid in by_id]
    ds = MultiLabelDataset(val_records, image_root=image_root, label_order=labels)
    loader = build_dataloader(ds, batch_size=32, shuffle=False)

    model = build_model(model_config)
    load_checkpoint(checkpoint, model=model, map_location="cpu")

    y_true, y_score = _collect(model, loader)
    out_dir = Path("ml/outputs/calibration")
    out_dir.mkdir(parents=True, exist_ok=True)

    method = args.method
    artifact = {}
    temperature = None
    if method == "temperature":
        # fit single temperature on first label for demo (use approved config to scope)
        scaler = TemperatureScaler()
        # take first column
        first = 0
        import torch

        # get logits quickly
        logits_list = []
        targets_list = []
        model.eval()
        for batch in loader:
            inputs, targets = batch
            with torch.no_grad():
                logits = model(inputs)
                if isinstance(logits, dict):
                    raise NotConfiguredError("single-output model required")
                logits_list.append(logits.detach().cpu())
                targets_list.append(targets.cpu())
        import numpy as np

        logits_arr = torch.cat(logits_list).numpy()
        targets_arr = torch.cat(targets_list).numpy()
        t = scaler.fit(logits_arr[:, first], targets_arr[:, first], binary=True)
        temperature = t
        artifact = {"method": "temperature", "temperature": t}
    else:
        calibrator = IsotonicCalibrator()
        calibrator.fit(y_true[:, 0], y_score[:, 0])
        artifact = {"method": "isotonic", "fitted": calibrator.fitted}

    report = build_calibration_report(y_true[:, 0], y_score[:, 0], method=method, temperature=temperature)
    (out_dir / "calibration-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (out_dir / "calibration-artifact.json").write_text(json.dumps(artifact, indent=2), encoding="utf-8")
    logger.info("calibration written to %s", out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
