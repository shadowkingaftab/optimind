"""Data cleaning utilities."""

from __future__ import annotations

from .corrupted_image_remover import CorruptionResult, find_corrupted
from .duplicate_detector import (
    DuplicateGroup,
    compute_dhash,
    find_exact_duplicates,
    find_near_duplicates,
)
from .label_cleaner import LabelCleanResult, clean_labels
from .metadata_cleaner import MetadataCleanResult, clean_metadata
from .outlier_detector import OutlierResult, detect_size_outliers

__all__ = [
    "CorruptionResult",
    "find_corrupted",
    "DuplicateGroup",
    "compute_dhash",
    "find_exact_duplicates",
    "find_near_duplicates",
    "LabelCleanResult",
    "clean_labels",
    "MetadataCleanResult",
    "clean_metadata",
    "OutlierResult",
    "detect_size_outliers",
]
