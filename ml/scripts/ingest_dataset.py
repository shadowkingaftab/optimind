#!/usr/bin/env python
"""Ingest a raw manifest into a normalised, validation-ready manifest.

Reads a manifest (CSV or JSON), cleans metadata fields, verifies provenance via
the source registry, and writes a canonical manifest plus an ingestion report.
The script never downloads data and never fabricates records; if the source
registry or required provenance is missing it exits with a clear message.

Usage:
    python ml/scripts/ingest_dataset.py --config ml/configs/datasets/fundus_dataset.yaml \
        --manifest datasets/metadata/images.csv --output datasets/interim/manifest.csv
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

from eyedx_ml.data.cleaning.metadata_cleaner import clean_metadata
from eyedx_ml.data.ingestion import (
    DatasetError,
    SourceError,
    load_source_registry,
    read_manifest,
    write_manifest,
)
from eyedx_ml.utils.config_loader import ConfigError, load_config
from eyedx_ml.utils.logging import get_logger

logger = get_logger("eyedx_ml.ingest")


def _load_config(path: str) -> dict:
    try:
        return load_config(path)
    except ConfigError as exc:
        logger.error("configuration error: %s", exc)
        raise SystemExit(2)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, help="dataset config YAML")
    parser.add_argument("--manifest", help="override manifest path")
    parser.add_argument("--output", help="override output manifest path")
    parser.add_argument(
        "--registry", help="override source registry directory or file"
    )
    args = parser.parse_args(argv)

    config = _load_config(args.config)
    paths = config.get("paths", {})
    source = config.get("source", {})

    manifest_path = args.manifest or paths.get("manifest")
    if not manifest_path:
        logger.error(
            "no manifest configured; set paths.manifest or pass --manifest"
        )
        return 2

    registry_path = args.registry or source.get("registry")
    if registry_path:
        try:
            load_source_registry(registry_path)
        except (SourceError, FileNotFoundError) as exc:
            logger.error(
                "source registry not usable (%s); provide licensed, approved "
                "sources under datasets/external before ingesting",
                exc,
            )
            return 3
    elif source.get("require_license", True):
        logger.error(
            "no source registry configured; a registered licence is required "
            "before ingestion"
        )
        return 3

    try:
        records = read_manifest(manifest_path)
    except DatasetError as exc:
        logger.error("could not read manifest: %s", exc)
        return 4

    if not records:
        logger.error("manifest contains no records")
        return 4

    clean_result = clean_metadata(records)
    output_path = args.output or Path(paths.get("output_dir", "datasets/interim")) / "manifest.csv"
    write_manifest(output_path, records)

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "manifest_in": Path(manifest_path).name,
        "manifest_out": Path(output_path).name,
        "records": len(records),
        "metadata_cleaning": clean_result.as_dict(),
        "note": "no data was downloaded or copied by this step",
    }
    report_path = Path(output_path).with_suffix(".ingest.json")
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    logger.info(
        "ingested %d records; wrote %s", len(records), Path(output_path).name
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
