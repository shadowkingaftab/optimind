#!/usr/bin/env python
"""Compute dataset statistics and write a datasheet-companion report.

Aggregates class distribution, image statistics and (optionally) demographic
statistics with small-cell suppression. Image probing runs only when --images is
given. The report contains aggregate values only, never patient identifiers or
pixel data.

Usage:
    python ml/scripts/calculate_statistics.py --config ml/configs/datasets/fundus_dataset.yaml \
        --manifest datasets/interim/manifest.csv [--images] [--report datasets/statistics.json]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from eyedx_ml.data.ingestion import (
    DatasetError,
    load_label_map,
    load_metadata_tables,
    read_manifest,
)
from eyedx_ml.data.statistics import (
    build_dataset_report,
    compute_class_distribution,
    compute_demographic_statistics,
    compute_image_statistics,
    write_dataset_report,
)
from eyedx_ml.utils.config_loader import ConfigError, load_config
from eyedx_ml.utils.logging import get_logger

logger = get_logger("eyedx_ml.stats")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--manifest")
    parser.add_argument("--images", action="store_true")
    parser.add_argument("--sample-limit", type=int, default=None)
    parser.add_argument("--report", help="output report path (JSON)")
    args = parser.parse_args(argv)

    try:
        config = load_config(args.config)
    except ConfigError as exc:
        logger.error("configuration error: %s", exc)
        return 2

    paths = config.get("paths", {})
    stats_cfg = config.get("statistics", {})
    manifest_path = args.manifest or paths.get("manifest")
    if not manifest_path:
        logger.error("no manifest configured; pass --manifest")
        return 2

    try:
        records = read_manifest(manifest_path)
    except DatasetError as exc:
        logger.error("could not read manifest: %s", exc)
        return 4

    display_names = {}
    label_map_path = paths.get("label_map")
    if label_map_path and Path(label_map_path).is_file():
        try:
            label_map = load_label_map(label_map_path)
            display_names = {d.code: (d.display_name or d.code) for d in label_map.labels}
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("could not load label map: %s", exc)

    distribution = compute_class_distribution(records, display_names=display_names)

    image_stats = None
    image_root = paths.get("image_root")
    if args.images and image_root:
        limit = args.sample_limit or stats_cfg.get("sample_limit")
        if isinstance(limit, str):
            limit = None
        image_stats = compute_image_statistics(records, image_root=image_root, limit=limit)
    elif args.images:
        logger.warning("no image_root configured; skipping image statistics")

    demographic = None
    metadata_dir = paths.get("metadata_dir")
    if metadata_dir and Path(metadata_dir).is_dir():
        try:
            tables = load_metadata_tables(metadata_dir)
            demographic = compute_demographic_statistics(
                tables, min_cell_size=int(stats_cfg.get("min_cell_size", 5))
            )
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("could not compute demographic statistics: %s", exc)

    report = build_dataset_report(
        records,
        class_distribution=distribution,
        image_statistics=image_stats,
        demographic_statistics=demographic,
        metadata={"source_manifest": Path(manifest_path).name},
    )

    report_path = (
        Path(args.report)
        if args.report
        else Path(manifest_path).with_suffix(".statistics.json")
    )
    write_dataset_report(report_path, report)

    logger.info(
        "statistics: records=%d patients=%d labels=%d",
        report["record_count"],
        report["patient_count"],
        len(distribution.per_label),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
