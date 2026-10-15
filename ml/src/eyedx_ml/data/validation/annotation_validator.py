"""Annotation validation.

Checks label coverage and consistency against the approved label map: every
record should be labelled, codes must be known, and binary values must be 0/1
(unless the task is explicitly probabilistic).
"""

from __future__ import annotations

from typing import Collection, Optional, Sequence

from eyedx_ml.data.ingestion.dataset_importer import DatasetRecord
from eyedx_ml.data.validation.integrity_report import ValidationReport

__all__ = ["validate_annotations"]


def validate_annotations(
    records: Sequence[DatasetRecord],
    *,
    known_codes: Optional[Collection[str]] = None,
    allow_probabilities: bool = False,
    require_at_least_one: bool = True,
) -> ValidationReport:
    """Validate labels on manifest records."""
    report = ValidationReport(checked=len(records))
    known = set(known_codes) if known_codes is not None else None

    for index, record in enumerate(records):
        ctx = {"index": index}
        if not record.labels:
            if require_at_least_one:
                report.warning("no_labels", "record has no labels", **ctx)
            continue
        for code, value in record.labels.items():
            if known is not None and code not in known:
                report.error(
                    "unknown_label_code", f"label code not in map: {code}", **ctx
                )
            if not isinstance(value, (int, float)):
                report.error(
                    "non_numeric_label", f"label {code} is not numeric", **ctx
                )
                continue
            if allow_probabilities:
                if not 0.0 <= float(value) <= 1.0:
                    report.error(
                        "label_out_of_range",
                        f"label {code} outside [0,1]",
                        **ctx,
                    )
            elif float(value) not in (0.0, 1.0):
                report.error(
                    "non_binary_label",
                    f"label {code} is not 0/1",
                    **ctx,
                )
    return report
