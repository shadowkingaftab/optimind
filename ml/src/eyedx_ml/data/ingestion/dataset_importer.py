"""Dataset manifest import/export.

Reads a canonical manifest (CSV or JSON) describing images and their metadata,
producing :class:`DatasetRecord` objects. Paths are stored relative to the image
root; absolute patient data is never copied or committed here.

Canonical manifest columns are defined in ``MANIFEST_COLUMNS`` and validated by
the metadata validator. Pseudonymous ``patient_key`` values (not raw ids) are
required for leakage-safe splits.
"""

from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Union

__all__ = [
    "DatasetError",
    "DatasetRecord",
    "MANIFEST_COLUMNS",
    "read_manifest",
    "write_manifest",
    "pseudonymize",
]

MANIFEST_COLUMNS: Sequence[str] = (
    "record_id",
    "image_path",
    "patient_key",
    "site_id",
    "device_id",
    "eye_side",
    "image_format",
    "checksum_sha256",
)


class DatasetError(ValueError):
    """Raised for malformed or missing dataset manifests."""


@dataclass
class DatasetRecord:
    record_id: str
    image_path: str
    patient_key: str
    site_id: Optional[str] = None
    device_id: Optional[str] = None
    eye_side: Optional[str] = None
    image_format: Optional[str] = None
    checksum_sha256: Optional[str] = None
    labels: Dict[str, float] = field(default_factory=dict)
    split: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_row(self) -> Dict[str, Any]:
        row = {
            "record_id": self.record_id,
            "image_path": self.image_path,
            "patient_key": self.patient_key,
            "site_id": self.site_id or "",
            "device_id": self.device_id or "",
            "eye_side": self.eye_side or "",
            "image_format": self.image_format or "",
            "checksum_sha256": self.checksum_sha256 or "",
        }
        if self.labels:
            row["labels"] = json.dumps(self.labels, sort_keys=True)
        if self.split:
            row["split"] = self.split
        return row


def pseudonymize(value: str, *, salt: str) -> str:
    """Return a stable, non-reversible key for a patient identifier.

    A deployment-specific salt (from configuration, never committed) ensures the
    resulting keys cannot be matched across datasets.
    """
    if not value:
        raise DatasetError("cannot pseudonymize empty value")
    if not salt or "INPUT_REQUIRED" in salt:
        raise DatasetError("a non-empty pseudonymization salt is required")
    digest = hashlib.sha256(f"{salt}:{value}".encode("utf-8")).hexdigest()
    return digest[:32]


def _require_columns(header: Sequence[str]) -> None:
    missing = [c for c in ("record_id", "image_path", "patient_key") if c not in header]
    if missing:
        raise DatasetError(f"manifest missing required columns: {missing}")


def read_manifest(
    path: Union[str, Path],
    *,
    default_split: Optional[str] = None,
) -> List[DatasetRecord]:
    """Read a CSV or JSON manifest into records."""
    file_path = Path(path)
    if not file_path.is_file():
        raise DatasetError(f"manifest not found: {file_path.name}")

    records: List[DatasetRecord] = []
    if file_path.suffix.lower() == ".json":
        payload = json.loads(file_path.read_text(encoding="utf-8"))
        entries = payload.get("entries") if isinstance(payload, dict) else payload
        if not isinstance(entries, list):
            raise DatasetError("JSON manifest must be a list or {'entries': [...]}")
        for entry in entries:
            records.append(_record_from_mapping(entry, default_split))
    else:
        with file_path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            _require_columns(reader.fieldnames or [])
            for row in reader:
                records.append(_record_from_row(row, default_split))
    return records


def _record_from_row(row: Mapping[str, str], default_split: Optional[str]) -> DatasetRecord:
    labels: Dict[str, float] = {}
    raw_labels = (row.get("labels") or "").strip()
    if raw_labels:
        try:
            parsed = json.loads(raw_labels)
            if isinstance(parsed, Mapping):
                labels = {str(k): float(v) for k, v in parsed.items()}
        except (ValueError, TypeError) as exc:
            raise DatasetError("labels column must be a JSON object") from exc

    extra = {
        k: v
        for k, v in row.items()
        if k not in MANIFEST_COLUMNS and k not in ("labels", "split") and v not in (None, "")
    }
    return DatasetRecord(
        record_id=str(row.get("record_id", "")).strip(),
        image_path=str(row.get("image_path", "")).strip(),
        patient_key=str(row.get("patient_key", "")).strip(),
        site_id=_clean(row.get("site_id")),
        device_id=_clean(row.get("device_id")),
        eye_side=_clean(row.get("eye_side")),
        image_format=_clean(row.get("image_format")),
        checksum_sha256=_clean(row.get("checksum_sha256")),
        labels=labels,
        split=_clean(row.get("split")) or default_split,
        metadata=extra,
    )


def _record_from_mapping(entry: Mapping[str, Any], default_split: Optional[str]) -> DatasetRecord:
    if not isinstance(entry, Mapping):
        raise DatasetError("each JSON entry must be an object")
    return DatasetRecord(
        record_id=str(entry.get("record_id", "")).strip(),
        image_path=str(entry.get("image_path", "")).strip(),
        patient_key=str(entry.get("patient_key", "")).strip(),
        site_id=entry.get("site_id"),
        device_id=entry.get("device_id"),
        eye_side=entry.get("eye_side"),
        image_format=entry.get("image_format"),
        checksum_sha256=entry.get("checksum_sha256"),
        labels={str(k): float(v) for k, v in (entry.get("labels") or {}).items()},
        split=entry.get("split") or default_split,
        metadata=entry.get("metadata") or {},
    )


def _clean(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    value = str(value).strip()
    return value or None


def write_manifest(
    path: Union[str, Path],
    records: Iterable[DatasetRecord],
    *,
    include_labels: bool = True,
) -> None:
    """Write records to a CSV manifest (atomic-ish overwrite)."""
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    columns = list(MANIFEST_COLUMNS)
    if include_labels:
        columns.append("labels")
    columns.append("split")
    with file_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for record in records:
            writer.writerow(record.to_row())
