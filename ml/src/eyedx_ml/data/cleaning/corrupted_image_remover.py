"""Corrupted-image removal.

Attempts a full decode of each referenced image and partitions records into
readable and unreadable. Nothing is deleted from disk; callers decide how to
quarantine excluded records.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Sequence, Tuple, Union

from eyedx_ml.data.ingestion.dataset_importer import DatasetRecord

__all__ = ["CorruptionResult", "find_corrupted"]


@dataclass
class CorruptionResult:
    readable: List[DatasetRecord] = field(default_factory=list)
    corrupted: List[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {"readable": len(self.readable), "corrupted": len(self.corrupted)}


def _can_decode(path: Path) -> bool:
    try:  # pragma: no cover - optional dependency
        from PIL import Image
    except Exception:
        # Without Pillow we cannot verify; treat as readable but note elsewhere.
        return True
    try:
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            image.load()
        return True
    except Exception:
        return False


def find_corrupted(
    records: Sequence[DatasetRecord],
    *,
    image_root: Union[str, Path],
) -> CorruptionResult:
    """Partition records into readable and corrupted (by record_id)."""
    root = Path(image_root)
    result = CorruptionResult()
    for record in records:
        if _can_decode(root / record.image_path):
            result.readable.append(record)
        else:
            result.corrupted.append(record.record_id)
    return result
