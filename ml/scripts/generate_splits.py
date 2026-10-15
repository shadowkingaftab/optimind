#!/usr/bin/env python
"""Generate reproducible, leakage-safe dataset splits.

Splits a manifest by patient (default) or by site (leave-site-out) using the
ratios and seed from the dataset config, then writes per-split CSVs and a
split manifest recording assignments, counts and the input checksum. Patients
never span splits. No data is copied.

Usage:
    python ml/scripts/generate_splits.py --config ml/configs/datasets/fundus_dataset.yaml \
        --manifest datasets/interim/manifest.csv --output-dir datasets/splits
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from eyedx_ml.data.ingestion import DatasetError, read_manifest
from eyedx_ml.data.splitting import (
    split_by_patient,
    split_by_site,
    write_split_csvs,
)
from eyedx_ml.utils.config_loader import ConfigError, load_config
from eyedx_ml.utils.logging import get_logger

logger = get_logger("eyedx_ml.splits")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--manifest")
    parser.add_argument("--output-dir")
    parser.add_argument("--strategy", choices=["patient", "site"], default=None)
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args(argv)

    try:
        config = load_config(args.config)
    except ConfigError as exc:
        logger.error("configuration error: %s", exc)
        return 2

    paths = config.get("paths", {})
    splitting = config.get("splitting", {})
    labels = config.get("labels", {})

    manifest_path = args.manifest or paths.get("manifest")
    if not manifest_path:
        logger.error("no manifest configured; pass --manifest")
        return 2

    try:
        records = read_manifest(manifest_path)
    except DatasetError as exc:
        logger.error("could not read manifest: %s", exc)
        return 4

    ratios = splitting.get("ratios") or {"train": 0.7, "validation": 0.15, "test": 0.15}
    seed = args.seed if args.seed is not None else int(splitting.get("seed", 42))
    strategy = args.strategy or splitting.get("strategy", "patient")
    stratify_on = splitting.get("stratify_on")
    if isinstance(stratify_on, str) and "INPUT_REQUIRED" in stratify_on:
        stratify_on = None

    try:
        if strategy == "site":
            holdout = splitting.get("holdout_sites") or []
            if not holdout:
                logger.error(
                    "site splitting requires splitting.holdout_sites to be set"
                )
                return 3
            result = split_by_site(
                records,
                holdout_sites=holdout,
                ratios=ratios,
                seed=seed,
                stratify_label=stratify_on,
            )
        else:
            result = split_by_patient(
                records,
                ratios=ratios,
                seed=seed,
                stratify_label=stratify_on,
            )
    except (ValueError, KeyError) as exc:
        logger.error("could not generate splits: %s", exc)
        return 5

    output_dir = args.output_dir or paths.get("splits_dir", "datasets/splits")
    write_split_csvs(output_dir, records, result.record_split)
    manifest_out = Path(output_dir) / "split-manifest.json"
    result.manifest.write(manifest_out)

    logger.info(
        "wrote splits (strategy=%s seed=%d) to %s",
        strategy,
        seed,
        Path(output_dir).name,
    )
    logger.info("split counts: %s", json.dumps(result.manifest.split_counts))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
