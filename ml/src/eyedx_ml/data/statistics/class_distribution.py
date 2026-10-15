"""Class-distribution statistics.

Counts per-label prevalence overall and per split. When a label map is supplied,
codes are resolved to display names; otherwise codes are used as-is.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, Mapping, Optional, Sequence

from eyedx_ml.data.ingestion.dataset_importer import DatasetRecord

__all__ = ["ClassDistribution", "compute_class_distribution"]


@dataclass
class ClassDistribution:
    total_records: int = 0
    labelled_records: int = 0
    per_label: Dict[str, Dict[str, float]] = field(default_factory=dict)
    per_split: Dict[str, Dict[str, Dict[str, float]]] = field(default_factory=dict)
    display_names: Dict[str, str] = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {
            "total_records": self.total_records,
            "labelled_records": self.labelled_records,
            "per_label": self.per_label,
            "per_split": self.per_split,
            "display_names": self.display_names,
        }


def _accumulate(
    records: Sequence[DatasetRecord],
) -> Dict[str, Dict[str, float]]:
    totals: Dict[str, int] = defaultdict(int)
    positives: Dict[str, int] = defaultdict(int)
    for record in records:
        for code, value in (record.labels or {}).items():
            totals[code] += 1
            if float(value) >= 0.5:
                positives[code] += 1
    result: Dict[str, Dict[str, float]] = {}
    for code, total in totals.items():
        positive = positives.get(code, 0)
        result[code] = {
            "labelled": total,
            "positive": positive,
            "negative": total - positive,
            "prevalence": (positive / total) if total else 0.0,
        }
    return result


def compute_class_distribution(
    records: Sequence[DatasetRecord],
    *,
    display_names: Optional[Mapping[str, str]] = None,
) -> ClassDistribution:
    distribution = ClassDistribution(total_records=len(records))
    distribution.labelled_records = sum(1 for r in records if r.labels)
    distribution.per_label = _accumulate(records)

    by_split: Dict[str, list] = defaultdict(list)
    for record in records:
        by_split[record.split or "unassigned"].append(record)
    distribution.per_split = {
        split: _accumulate(split_records)
        for split, split_records in sorted(by_split.items())
    }

    if display_names:
        codes = set(distribution.per_label) | {
            code for d in distribution.per_split.values() for code in d
        }
        distribution.display_names = {
            code: display_names[code] for code in codes if code in display_names
        }
    return distribution
