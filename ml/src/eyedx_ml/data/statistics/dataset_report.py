"""Dataset report assembly.

Combines class distribution, image statistics, split counts and validation
results into a single JSON report suitable for committing as a datasheet
companion. Never embeds patient identifiers or pixel data.
"""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Sequence, Union

from eyedx_ml.data.ingestion.dataset_importer import DatasetRecord
from eyedx_ml.data.statistics.class_distribution import (
    ClassDistribution,
    compute_class_distribution,
)
from eyedx_ml.data.statistics.demographic_statistics import DemographicStatistics
from eyedx_ml.data.statistics.image_statistics import ImageStatistics
from eyedx_ml.data.validation.integrity_report import ValidationReport

__all__ = ["build_dataset_report", "write_dataset_report"]


def _coerce(value: Any) -> Any:
    if value is None:
        return None
    if hasattr(value, "as_dict"):
        return value.as_dict()
    if is_dataclass(value):
        return asdict(value)
    return value


def build_dataset_report(
    records: Sequence[DatasetRecord],
    *,
    class_distribution: Optional[ClassDistribution] = None,
    image_statistics: Optional[ImageStatistics] = None,
    demographic_statistics: Optional[DemographicStatistics] = None,
    validation: Optional[ValidationReport] = None,
    split_manifest: Optional[Mapping[str, Any]] = None,
    metadata: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """Assemble a dataset report dictionary."""
    distribution = class_distribution or compute_class_distribution(records)
    return {
        "schema_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "record_count": len(records),
        "patient_count": len({r.patient_key for r in records if r.patient_key}),
        "class_distribution": _coerce(distribution),
        "image_statistics": _coerce(image_statistics),
        "demographic_statistics": _coerce(demographic_statistics),
        "validation": validation.to_dict() if validation is not None else None,
        "split_manifest": dict(split_manifest) if split_manifest else None,
        "metadata": dict(metadata or {}),
    }


def write_dataset_report(
    path: Union[str, Path], report: Mapping[str, Any]
) -> None:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(
        json.dumps(report, indent=2, sort_keys=True, default=str), encoding="utf-8"
    )
