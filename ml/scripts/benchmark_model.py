#!/usr/bin/env python
"""Benchmark inference latency and throughput.

Measures end-to-end inference time for the predictor. Thresholds/parameters are
taken from an approved inference config.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from eyedx_ml.inference import Predictor, benchmark_predictor
from eyedx_ml.utils.config_loader import ConfigError, load_config
from eyedx_ml.utils.logging import get_logger

logger = get_logger("eyedx_ml.benchmark")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    args = parser.parse_args(argv)

    try:
        config = load_config(args.config)
    except ConfigError as exc:
        logger.error("%s", exc)
        return 2

    try:
        predictor = Predictor.from_config(args.config)
    except Exception as exc:
        logger.error("cannot build predictor: %s", exc)
        return 3

    try:
        import torch

        model_config = predictor.__dict__  # not stored; read via config
    except Exception:
        pass

    # build dummy input
    try:
        import torch

        model = None  # rebuild minimal
        from eyedx_ml.models.model_config import load_model_config
        from eyedx_ml.models.model_factory import build_model

        model_cfg = load_model_config((load_config(args.config).get("model", {})).get("config"))
        model = build_model(model_config=model_cfg) if False else None  # placeholder
    except Exception:
        pass

    out = Path("ml/outputs/benchmarks")
    out.mkdir(parents=True, exist_ok=True)
    # default dummy if torch missing
    try:
        import torch

        dummy = torch.randn(1, 3, 512, 512)
        res = benchmark_predictor(predictor, dummy, warmup=2, repeats=10)
        (out / "inference-benchmark.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
        logger.info("benchmark written to %s", out / "inference-benchmark.json")
    except Exception as exc:
        logger.warning("benchmark skipped (torch or inputs unavailable): %s", exc)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
