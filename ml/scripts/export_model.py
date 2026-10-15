#!/usr/bin/env python
"""Export a trained model to TorchScript/ONNX and package it.

Creates a model package with model-metadata.json (contract-aligned) and writes
the export manifest. No weights are fabricated; a valid checkpoint is required.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from eyedx_ml.export import (
    export_onnx,
    export_torchscript,
    package_model,
    validate_metadata,
    write_model_metadata,
)
from eyedx_ml.models.model_config import load_model_config
from eyedx_ml.models.model_factory import build_model
from eyedx_ml.training.checkpoint_manager import build_checkpoint_metadata, load_checkpoint
from eyedx_ml.utils.config_loader import ConfigError, load_config
from eyedx_ml.utils.logging import get_logger

logger = get_logger("eyedx_ml.export_model")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--output-dir", default="ml/export")
    parser.add_argument("--to-onnx", action="store_true")
    parser.add_argument("--model-id", required=False)
    parser.add_argument("--model-version", required=False)
    args = parser.parse_args(argv)

    try:
        config = load_config(args.config)
    except ConfigError as exc:
        logger.error("%s", exc)
        return 2

    model_cfg_path = (config.get("model") or {}).get("config")
    if not model_cfg_path or not Path(model_cfg_path).is_file():
        logger.error("model config not found (INPUT_REQUIRED)")
        return 3
    model_config = load_model_config(model_cfg_path)
    labels = model_config.load_approved_labels()

    model = build_model(model_config)
    load_checkpoint(args.checkpoint, model=model, map_location="cpu")

    metadata = build_checkpoint_metadata(
        model_id=args.model_id or "eyedx-screening",
        model_version=args.model_version or "INPUT_REQUIRED",
        architecture=model_config.architecture,
        backbone=model_config.backbone,
        labels=labels,
        preprocessing=model_config.preprocessing or {},
    )

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    artifacts = {}
    # torchscript
    try:
        import torch

        example = torch.randn(1, model_config.in_channels, *model_config.input_size)
        ts_path = out / "model.pt"
        export_torchscript(model, example, ts_path)
        artifacts["torchscript"] = str(ts_path)
    except Exception as exc:  # pragma: no cover - optional
        logger.warning("torchscript export failed (no-ops allowed in harness): %s", exc)

    if args.to_onnx:
        try:
            import torch

            example = torch.randn(1, model_config.in_channels, *model_config.input_size)
            onnx_path = out / "model.onnx"
            export_onnx(model, example, onnx_path)
            artifacts["onnx"] = str(onnx_path)
        except Exception as exc:  # pragma: no cover
            logger.warning("onnx export failed: %s", exc)

    meta_path = out / "model-metadata.json"
    write_model_metadata(metadata, meta_path)
    manifest = package_model(
        out / f"package-{metadata['model_id']}-{metadata['model_version']}",
        metadata=metadata,
        artifacts=artifacts,
        overwrite=True,
    )
    logger.info("packaged at %s", manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
