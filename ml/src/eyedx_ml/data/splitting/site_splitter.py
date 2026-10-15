"""Site-based (leave-site-out) splitting.

Holds out one or more clinical sites entirely for external-style validation,
which is a stronger test of generalisation than random splitting. Sites not
named for holdout are split by patient using the requested ratios.
"""

from __future__ import annotations

from typing import Dict, Mapping, Sequence

from eyedx_ml.data.ingestion.dataset_importer import DatasetRecord
from eyedx_ml.data.splitting.patient_splitter import PatientSplitResult, split_by_patient
from eyedx_ml.data.splitting.split_manifest import SplitManifest, build_split_manifest

__all__ = ["split_by_site"]


def split_by_site(
    records: Sequence[DatasetRecord],
    *,
    holdout_sites: Sequence[str],
    ratios: Mapping[str, float],
    seed: int = 42,
    holdout_split_name: str = "test",
    stratify_label: str | None = None,
) -> PatientSplitResult:
    """Assign held-out sites to ``holdout_split_name``; split the rest by patient."""
    holdout = set(holdout_sites)
    if not holdout:
        raise ValueError("holdout_sites must be non-empty for a site split")

    holdout_records = [r for r in records if (r.site_id or "") in holdout]
    remaining = [r for r in records if (r.site_id or "") not in holdout]
    if not remaining:
        raise ValueError("no records remain after removing holdout sites")

    inner = split_by_patient(
        remaining, ratios=ratios, seed=seed, stratify_label=stratify_label
    )

    record_split: Dict[str, str] = dict(inner.record_split)
    patient_split: Dict[str, str] = dict(inner.patient_split)
    for record in holdout_records:
        record.split = holdout_split_name
        record_split[record.record_id] = holdout_split_name
        patient_split[record.patient_key] = holdout_split_name

    manifest: SplitManifest = build_split_manifest(
        records,
        record_split,
        patient_split,
        ratios=ratios,
        seed=seed,
        notes=f"leave-site-out holdout={sorted(holdout)}",
    )
    return PatientSplitResult(
        manifest=manifest, record_split=record_split, patient_split=patient_split
    )
