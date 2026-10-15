"""Data splitting strategies."""

from __future__ import annotations

from .patient_splitter import PatientSplitResult, split_by_patient
from .site_splitter import split_by_site
from .split_manifest import SplitManifest, build_split_manifest, write_split_csvs
from .stratified_splitter import (
    SplitError,
    allocate_counts,
    stratified_split,
    validate_ratios,
)

__all__ = [
    "PatientSplitResult",
    "split_by_patient",
    "split_by_site",
    "SplitManifest",
    "build_split_manifest",
    "write_split_csvs",
    "SplitError",
    "allocate_counts",
    "stratified_split",
    "validate_ratios",
]
