"""Metadata cleaning.

Trims whitespace, normalises enumeration fields (eye side, image format) and
lowercases keys. Missing values are left as ``None``; the cleaner never invents
metadata.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Sequence

from eyedx_ml.data.ingestion.dataset_importer import DatasetRecord

__all__ = ["MetadataCleanResult", "clean_metadata"]

_EYE_SIDE_ALIASES = {
    "l": "left",
    "left": "left",
    "os": "left",
    "r": "right",
    "right": "right",
    "od": "right",
    "unknown": "unknown",
    "": "unknown",
}

_FORMAT_ALIASES = {
    "jpg": "jpeg",
    "jpeg": "jpeg",
    ".jpg": "jpeg",
    ".jpeg": "jpeg",
    "png": "png",
    ".png": "png",
}


@dataclass
class MetadataCleanResult:
    changes: int = 0
    unknown_eye_sides: int = 0
    unknown_formats: int = 0

    def as_dict(self) -> Dict[str, int]:
        return {
            "changes": self.changes,
            "unknown_eye_sides": self.unknown_eye_sides,
            "unknown_formats": self.unknown_formats,
        }


def clean_metadata(records: Sequence[DatasetRecord]) -> MetadataCleanResult:
    result = MetadataCleanResult()
    for record in records:
        side = (record.eye_side or "").strip().lower()
        normalized_side = _EYE_SIDE_ALIASES.get(side)
        if normalized_side is None:
            result.unknown_eye_sides += 1
            normalized_side = "unknown"
        if normalized_side != record.eye_side:
            record.eye_side = normalized_side
            result.changes += 1

        if record.image_format:
            fmt = record.image_format.strip().lower()
            normalized_fmt = _FORMAT_ALIASES.get(fmt)
            if normalized_fmt is None:
                result.unknown_formats += 1
            elif normalized_fmt != record.image_format:
                record.image_format = normalized_fmt
                result.changes += 1

        for attr in ("record_id", "image_path", "patient_key", "site_id", "device_id"):
            value = getattr(record, attr)
            if isinstance(value, str):
                stripped = value.strip()
                if stripped != value:
                    setattr(record, attr, stripped)
                    result.changes += 1
    return result
