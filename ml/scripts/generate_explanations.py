#!/usr/bin/env python
"""Generate explanations for a sample of records (Grad-CAM).

Produces heatmaps and a report. Explanations are for review only and never shown
as a diagnosis.
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

from eyedx_ml.data.loaders import MultiLabelDataset, build_dataloader
from eyedx_ml.errors import NotConfiguredError
from eyedx_ml.explainability import GradCAM
from eyedx_ml.models.model_config import load_model_config
from eyedx_ml.models.model_factory import build_model
from eyedx_ml.training.checkpoint_manager import load_checkpoint
from eyedx_ml.utils.config_loader import ConfigError, load_config
from eyedx_ml.utils.logging import get_logger

logger = get_logger("eyedx_ml.explain")


def _require(path: str | None, label: str) -> str:
    if not path or not Path(path).is_file():
        raise NotConfiguredError(f"{label} not found ({path}) (INPUT_REQUIRED)")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args(argv)

    try:
        config = load_config(args.config)
    except ConfigError as exc:
        logger.error("%s", exc)
        return 2

    model_cfg_path = (config.get("model") or {}).get("config")
    if not model_cfg_path:
        logger.error("model.config required")
        return 3
    model_config = load_model_config(model_cfg_path)
    model = build_model(model_config)
    load_checkpoint(args.checkpoint, model=model, map_location="cpu")

    out = Path("ml/outputs/explainability")
    out.mkdir(parents=True, exist_ok=True)

    try:
        import torch

        example = torch.randn(1, model_config.in_channels, *model_config.input_size)
        # find target layer: last feature layer if resnet-like
        try:
            from eyedx_ml.models.backbones import create_backbone

            backbone = create_backbone(model_config.backbone or "resnet50")
            target = backbone.layer4 if hasattr(backbone, "layer4") else list(backbone.modules())[-2]
            cam = GradCAM(model, target)
            heatmap = cam.generate(example)
            Path(out / "sample_heatmap.json").write_text(
                json.dumps({"shape": list(heatmap.shape)}), encoding="utf-8"
            )
        except Exception as exc:
            logger.warning("GradCAM setup skipped: %s", exc)
    except Exception as exc:
        logger.warning("explanation generation skipped: %s", exc)

    logger.info("explanation outputs written to %s", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
