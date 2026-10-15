"""Calibration report assembly."""

from __future__ import annotations

from typing import Any, Dict, Optional

import numpy as np

from eyedx_ml.calibration.reliability_diagram import reliability_data
from eyedx_ml.metrics.calibration import (
    brier_score,
    expected_calibration_error,
    maximum_calibration_error,
)

__all__ = ["build_calibration_report"]


def build_calibration_report(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    *,
    n_bins: int = 10,
    method: Optional[str] = None,
    temperature: Optional[float] = None,
) -> Dict[str, Any]:
    """Assemble calibration metrics and reliability bins for a set of predictions."""
    y_true = np.asarray(y_true, dtype=float).ravel()
    y_prob = np.asarray(y_prob, dtype=float).ravel()
    report: Dict[str, Any] = {
        "n_samples": int(y_true.size),
        "method": method,
        "n_bins": n_bins,
        "expected_calibration_error": expected_calibration_error(y_true, y_prob, n_bins=n_bins),
        "maximum_calibration_error": maximum_calibration_error(y_true, y_prob, n_bins=n_bins),
        "brier_score": brier_score(y_true, y_prob),
        "reliability": reliability_data(y_true, y_prob, n_bins=n_bins),
    }
    if temperature is not None:
        report["temperature"] = float(temperature)
    return report
