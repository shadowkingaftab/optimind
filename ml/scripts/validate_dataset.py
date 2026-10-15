#!/usr/bin/env python
"""Validate a dataset manifest against its contract.

Runs metadata, annotation and leakage validation and, optionally, probes a
sample of images. Writes a JSON validation report and returns a non-zero exit
code when any error-level issue is found. No data is modified.

Usage:
    python ml/scripts/validate_dataset.py --config ml/configs/datasets/fundus_dataset.yaml \
        --manifest datasets/interim/manifest.csv [--images --sample-limit 200]
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from eyedx_ml.data.ingestion import (
    DatasetError,
    load_label_map,
    read_manifest,
)
from eyedx_ml.data.validation import (
    detect_leakage,
    validate_annotations,
    validate_image_records,
    validate_metadata,
)
from eyedx_ml.utils.config_loader import ConfigError, load_config
from eyedx_ml.utils.logging import get_logger

logger = get_logger("eyedx_ml.validate")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--manifest")
    parser.add_argument("--images", action="store_true", help="probe image contents")
    parser.add_argument("--sample-limit", type=int, default=None)
    parser.add_argument("--report", help="output report path (JSON)")
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

    known_codes = None
    label_map_path = paths.get("label_map")
    if label_map_path and Path(label_map_path).is_file():
        try:
            known_codes = {label.code for label in load_label_map(label_map_path).labels}
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("could not load label map: %s", exc)

    report = validate_metadata(
        records, require_labels=bool(config.get("validation", {}).get("require_labels"))
    )
    report.merge(validate_annotations(records, known_codes=known_codes))
    report.merge(detect_leakage(records))

    if args.images:
        image_root = paths.get("image_root")
        if not image_root:
            logger.warning("no image_root configured; skipping image probing")
        else:
            report.merge(
                validate_image_records(
                    records, image_root=image_root, limit=args.sample_limit
                )
            )

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "manifest": Path(manifest_path).name,
        "images_probed": bool(args.images),
        "validation": report.to_dict(),
    }
    report_path = (
        Path(args.report)
        if args.report
        else Path(manifest_path).with_suffix(".validation.json")
    )
    report_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    logger.info(
        "validation checked=%d errors=%d warnings=%d ok=%s",
        report.checked,
        len(report.errors),
        len(report.warnings),
        report.ok,
    )
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
