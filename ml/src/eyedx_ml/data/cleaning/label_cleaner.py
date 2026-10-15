"""Label cleaning.

Normalises label values and drops entries that the approved label map marks as
ignored. Unknown codes are reported rather than silently accepted. Cleaning is
explicit and conservative: it never infers a missing label.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Collection, Dict, List, Optional, Sequence

from eyedx_ml.data.ingestion.dataset_importer import DatasetRecord

__all__ = ["LabelCleanResult", "clean_labels"]


@dataclass
class LabelCleanResult:
    changes: int = 0
    dropped_codes: List[str] = field(default_factory=list)
    unknown_codes: List[str] = field(default_factory=list)
    records_missing_labels: int = 0

    def as_dict(self) -> Dict[str, object]:
        return {
            "changes": self.changes,
            "dropped_codes": sorted(set(self.dropped_codes)),
            "unknown_codes": sorted(set(self.unknown_codes)),
            "records_missing_labels": self.records_missing_labels,
        }


def _normalize_value(value: object, *, binarize: bool, threshold: float) -> float:
    try:
        numeric = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return 0.0
    if binarize:
        return 1.0 if numeric >= threshold else 0.0
    return numeric


def clean_labels(
    records: Sequence[DatasetRecord],
    *,
    known_codes: Optional[Collection[str]] = None,
    drop_codes: Optional[Collection[str]] = None,
    binarize: bool = False,
    threshold: float = 0.5,
) -> LabelCleanResult:
    """Clean labels in place and return a summary of what changed."""
    known = set(known_codes) if known_codes is not None else None
    drop = set(drop_codes or ())
    result = LabelCleanResult()

    for record in records:
        if not record.labels:
            result.records_missing_labels += 1
            continue
        cleaned: Dict[str, float] = {}
        for code, value in record.labels.items():
            if code in drop:
                result.dropped_codes.append(code)
                result.changes += 1
                continue
            if known is not None and code not in known:
                result.unknown_codes.append(code)
                result.changes += 1
                continue
            new_value = _normalize_value(value, binarize=binarize, threshold=threshold)
            if new_value != value:
                result.changes += 1
            cleaned[code] = new_value
        record.labels = cleaned

    return result
