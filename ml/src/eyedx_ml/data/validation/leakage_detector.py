"""Leakage detection.

Detects two classes of leakage:
  1. Patient leakage — the same ``patient_key`` appearing in more than one split.
  2. Duplicate leakage — identical image checksums (and optionally perceptual
     hashes) across splits.

The detector never logs patient identifiers; it reports counts and split names.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Optional, Sequence, Tuple

from eyedx_ml.data.ingestion.dataset_importer import DatasetRecord
from eyedx_ml.data.validation.integrity_report import ValidationReport

__all__ = ["detect_patient_leakage", "detect_duplicate_leakage", "detect_leakage"]


def detect_patient_leakage(
    records: Sequence[DatasetRecord],
) -> Tuple[ValidationReport, Dict[str, List[str]]]:
    """Return a report and a mapping of patient_key -> splits it appears in."""
    report = ValidationReport(checked=len(records))
    patient_splits: Dict[str, set[str]] = defaultdict(set)
    for record in records:
        split = record.split or "unassigned"
        patient_splits[record.patient_key].add(split)

    leaks = {p: sorted(s) for p, s in patient_splits.items() if len(s) > 1}
    for _patient, splits in leaks.items():
        report.error(
            "patient_split_leakage",
            "patient appears in multiple splits",
            splits=splits,
        )
    if leaks:
        report.info(
            "patient_leakage_summary", f"{len(leaks)} patients span multiple splits"
        )
    return report, leaks


def detect_duplicate_leakage(
    records: Sequence[DatasetRecord],
    *,
    perceptual_hashes: Optional[Dict[str, str]] = None,
) -> ValidationReport:
    """Detect identical images (by checksum or perceptual hash) across splits."""
    report = ValidationReport(checked=len(records))

    def _cross_split(index: Dict[str, set[str]], key_type: str) -> None:
        for _key, splits in index.items():
            if len(splits) > 1:
                report.error(
                    f"duplicate_{key_type}_across_splits",
                    f"identical {key_type} appears in multiple splits",
                    splits=sorted(splits),
                )

    by_checksum: Dict[str, set[str]] = defaultdict(set)
    for record in records:
        if record.checksum_sha256:
            by_checksum[record.checksum_sha256].add(record.split or "unassigned")
    _cross_split(by_checksum, "checksum")

    if perceptual_hashes:
        by_phash: Dict[str, set[str]] = defaultdict(set)
        for record in records:
            phash = perceptual_hashes.get(record.record_id)
            if phash:
                by_phash[phash].add(record.split or "unassigned")
        _cross_split(by_phash, "perceptual_hash")

    return report


def detect_leakage(
    records: Sequence[DatasetRecord],
    *,
    perceptual_hashes: Optional[Dict[str, str]] = None,
) -> ValidationReport:
    """Combined patient + duplicate leakage report."""
    patient_report, _ = detect_patient_leakage(records)
    dup_report = detect_duplicate_leakage(
        records, perceptual_hashes=perceptual_hashes
    )
    patient_report.merge(dup_report)
    return patient_report
