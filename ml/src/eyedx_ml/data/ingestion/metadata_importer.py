"""Metadata table import.

Loads non-image metadata tables (patients, sites, devices) and validates their
required columns. These tables contain only pseudonymous keys and coarse,
non-identifying attributes (for example an age bucket), never direct
identifiers.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Union

from eyedx_ml.utils.logging import get_logger

__all__ = [
    "MetadataError",
    "MetadataTable",
    "REQUIRED_COLUMNS",
    "load_metadata_table",
    "load_metadata_tables",
]

logger = get_logger(__name__)

REQUIRED_COLUMNS: Dict[str, Sequence[str]] = {
    "patients": ("patient_key",),
    "clinical-sites": ("site_id",),
    "acquisition-devices": ("device_id",),
    "images": ("record_id", "image_path", "patient_key"),
}


class MetadataError(ValueError):
    """Raised for missing files or columns in metadata tables."""


@dataclass
class MetadataTable:
    name: str
    columns: List[str] = field(default_factory=list)
    rows: List[Dict[str, str]] = field(default_factory=list)

    def index_by(self, key: str) -> Dict[str, Dict[str, str]]:
        if key not in self.columns:
            raise MetadataError(f"table {self.name} has no column {key}")
        return {row[key]: row for row in self.rows if row.get(key)}


def load_metadata_table(path: Union[str, Path], *, name: Optional[str] = None) -> MetadataTable:
    file_path = Path(path)
    if not file_path.is_file():
        raise MetadataError(f"metadata table not found: {file_path.name}")
    table_name = name or file_path.stem
    with file_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        columns = list(reader.fieldnames or [])
        required = REQUIRED_COLUMNS.get(table_name, ())
        missing = [c for c in required if c not in columns]
        if missing:
            raise MetadataError(f"table {table_name} missing columns: {missing}")
        rows = [dict(r) for r in reader]
    logger.info("loaded metadata table %s (%d rows)", table_name, len(rows))
    return MetadataTable(name=table_name, columns=columns, rows=rows)


def load_metadata_tables(metadata_dir: Union[str, Path]) -> Dict[str, MetadataTable]:
    """Load all recognised metadata tables present in a directory."""
    directory = Path(metadata_dir)
    if not directory.is_dir():
        raise MetadataError(f"metadata directory not found: {directory.name}")
    tables: Dict[str, MetadataTable] = {}
    for name in REQUIRED_COLUMNS:
        candidate = directory / f"{name}.csv"
        if candidate.is_file():
            tables[name] = load_metadata_table(candidate, name=name)
    return tables
