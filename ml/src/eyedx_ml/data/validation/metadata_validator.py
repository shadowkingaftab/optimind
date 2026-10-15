"""Manifest and metadata validation.

Validates that a manifest's records are well-formed and internally consistent:
required fields present, no duplicate record ids, valid eye sides, and known
site/device references. Emits a :class:`ValidationReport`; it does not modify
data or touch image bytes.
"""

from __future__ import annotations

from typing import Collection, Iterable, Mapping, Optional, Sequence

from eyedx_ml.data.ingestion.dataset_importer import DatasetRecord
from eyedx_ml.data.validation.integrity_report import ValidationReport

__all__ = ["validate_metadata", "VALID_EYE_SIDES"]

VALID_EYE_SIDES = frozenset({"left", "right", "unknown", ""})


def validate_metadata(
    records: Sequence[DatasetRecord],
    *,
    known_sites: Optional[Collection[str]] = None,
    known_devices: Optional[Collection[str]] = None,
    require_labels: bool = False,
) -> ValidationReport:
    """Validate manifest records and return an aggregated report."""
    report = ValidationReport(checked=len(records))
    seen_ids: set[str] = set()

    for index, record in enumerate(records):
        ctx = {"index": index}

        if not record.record_id:
            report.error("missing_record_id", "record is missing record_id", **ctx)
        elif record.record_id in seen_ids:
            report.error(
                "duplicate_record_id", "duplicate record_id in manifest", **ctx
            )
        else:
            seen_ids.add(record.record_id)

        if not record.image_path:
            report.error("missing_image_path", "record has no image_path", **ctx)
        if not record.patient_key:
            report.error(
                "missing_patient_key",
                "record has no patient_key (required for leakage-safe splits)",
                **ctx,
            )

        side = (record.eye_side or "").strip().lower()
        if side not in VALID_EYE_SIDES:
            report.warning(
                "unknown_eye_side", f"unrecognised eye_side: {side!r}", **ctx
            )

        if known_sites is not None and record.site_id and record.site_id not in known_sites:
            report.warning(
                "unknown_site", "site_id not present in site table", **ctx
            )
        if (
            known_devices is not None
            and record.device_id
            and record.device_id not in known_devices
        ):
            report.warning(
                "unknown_device", "device_id not present in device table", **ctx
            )

        if require_labels and not record.labels:
            report.warning("missing_labels", "record has no labels", **ctx)

    return report
