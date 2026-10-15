"""Model evaluation and reporting."""

from __future__ import annotations

from .confusion_analysis import confusion_matrices
from .device_analysis import device_metrics
from .error_analysis import error_cases, error_summary
from .evaluation_report import build_evaluation_report, write_report
from .evaluator import Evaluator, compute_label_metrics
from .external_validation import run_external_validation
from .site_analysis import site_consistency, site_metrics
from .subgroup_analysis import subgroup_metrics

__all__ = [
    "Evaluator",
    "compute_label_metrics",
    "build_evaluation_report",
    "write_report",
    "subgroup_metrics",
    "site_metrics",
    "site_consistency",
    "device_metrics",
    "error_cases",
    "error_summary",
    "confusion_matrices",
    "run_external_validation",
]
