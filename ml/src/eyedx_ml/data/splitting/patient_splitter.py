"""Patient-level splitting.

All images belonging to one patient stay in exactly one split. Patients are
stratified by a configurable label so disease prevalence is approximately
preserved across splits. This is the default split strategy for clinical data
to prevent patient leakage.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Mapping, Optional, Sequence

from eyedx_ml.data.ingestion.dataset_importer import DatasetRecord
from eyedx_ml.data.splitting.split_manifest import (
    SplitManifest,
    build_split_manifest,
)
from eyedx_ml.data.splitting.stratified_splitter import stratified_split

__all__ = ["PatientSplitResult", "split_by_patient"]


@dataclass
class PatientSplitResult:
    manifest: SplitManifest
    record_split: Dict[str, str]
    patient_split: Dict[str, str]


def _patient_stratum(
    labels: List[Dict[str, float]], stratify_label: Optional[str]
) -> str:
    if stratify_label is None:
        return "all"
    for label in labels:
        if label.get(stratify_label, 0.0) >= 0.5:
            return "positive"
    return "negative"


def split_by_patient(
    records: Sequence[DatasetRecord],
    *,
    ratios: Mapping[str, float],
    seed: int = 42,
    stratify_label: Optional[str] = None,
    version: str = "1.0.0",
    notes: Optional[str] = None,
) -> PatientSplitResult:
    """Split records so that patients never span splits."""
    if not records:
        raise ValueError("no records to split")

    patients: Dict[str, List[DatasetRecord]] = defaultdict(list)
    for record in records:
        if not record.patient_key:
            raise ValueError("all records require a patient_key for patient splits")
        patients[record.patient_key].append(record)

    strata: Dict[str, List[str]] = defaultdict(list)
    for patient_key, patient_records in patients.items():
        stratum = _patient_stratum(
            [r.labels for r in patient_records], stratify_label
        )
        strata[stratum].append(patient_key)

    patient_split = stratified_split(strata, ratios, seed=seed)

    record_split: Dict[str, str] = {}
    for patient_key, split in patient_split.items():
        for record in patients[patient_key]:
            record.split = split
            record_split[record.record_id] = split

    manifest = build_split_manifest(
        records,
        record_split,
        patient_split,
        ratios=ratios,
        seed=seed,
        version=version,
        notes=notes or ("stratified by " + (stratify_label or "none")),
    )
    return PatientSplitResult(
        manifest=manifest, record_split=record_split, patient_split=patient_split
    )
