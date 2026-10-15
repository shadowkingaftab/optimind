#!/usr/bin/env python
"""Audit a manifest for duplicates, corruption and outliers.

Produces a cleaning report and an exclude list; it never deletes or modifies
image files. Excluded record ids are written to a CSV that downstream steps can
apply. Image-dependent checks run only when --images is given.

Usage:
    python ml/scripts/clean_dataset.py --config ml/configs/datasets/fundus_dataset.yaml \
        --manifest datasets/interim/manifest.csv [--images] [--sample-limit 500]
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from eyedx_ml.data.cleaning import (
    find_corrupted,
    find_exact_duplicates,
    find_near_duplicates,
)
from eyedx_ml.data.ingestion import DatasetError, read_manifest
from eyedx_ml.utils.config_loader import ConfigError, load_config
from eyedx_ml.utils.logging import get_logger

logger = get_logger("eyedx_ml.clean")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--manifest")
    parser.add_argument("--images", action="store_true")
    parser.add_argument("--sample-limit", type=int, default=None)
    parser.add_argument("--exclude-out", help="path to write excluded record ids")
    parser.add_argument("--report-out", help="path to write the cleaning report")
    args = parser.parse_args(argv)

    try:
        config = load_config(args.config)
    except ConfigError as exc:
        logger.error("configuration error: %s", exc)
        return 2

    paths = config.get("paths", {})
    manifest_path = args.manifest or paths.get("manifest")
    if not manifest_path:
        logger.error("no manifest configured; pass --manifest")
        return 2

    try:
        records = read_manifest(manifest_path)
    except DatasetError as exc:
        logger.error("could not read manifest: %s", exc)
        return 4

    exact_groups = find_exact_duplicates(records)
    exact_dupes = [rid for group in exact_groups for rid in group.duplicates]

    near_groups = []
    corrupted: list[str] = []
    image_root = paths.get("image_root")
    if args.images and image_root:
        selected = records if args.sample_limit is None else records[: args.sample_limit]
        near_groups = find_near_duplicates(selected, image_root=image_root)
        corrupted = find_corrupted(selected, image_root=image_root).corrupted
    elif args.images and not image_root:
        logger.warning("no image_root configured; skipping image checks")

    near_dupes = [rid for group in near_groups for rid in group.duplicates]
    excluded = sorted(set(exact_dupes) | set(near_dupes) | set(corrupted))

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "manifest": Path(manifest_path).name,
        "records": len(records),
        "images_checked": bool(args.images and image_root),
        "exact_duplicate_groups": [g.as_dict() for g in exact_groups],
        "near_duplicate_groups": [g.as_dict() for g in near_groups],
        "corrupted": corrupted,
        "excluded_count": len(excluded),
        "note": "no files were deleted or modified by this step",
    }

    report_path = (
        Path(args.report_out)
        if args.report_out
        else Path(manifest_path).with_suffix(".cleaning.json")
    )
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    exclude_path = (
        Path(args.exclude_out)
        if args.exclude_out
        else Path(manifest_path).with_suffix(".exclude.csv")
    )
    with exclude_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["record_id", "reason"])
        for rid in exact_dupes:
            writer.writerow([rid, "exact_duplicate"])
        for rid in near_dupes:
            writer.writerow([rid, "near_duplicate"])
        for rid in corrupted:
            writer.writerow([rid, "corrupted"])

    logger.info(
        "cleaning: exact=%d near=%d corrupted=%d excluded=%d",
        len(exact_dupes),
        len(near_dupes),
        len(corrupted),
        len(excluded),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
