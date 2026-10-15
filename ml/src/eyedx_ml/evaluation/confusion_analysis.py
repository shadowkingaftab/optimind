"""Confusion-matrix analysis."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import numpy as np

from eyedx_ml.metrics.classification import confusion_matrix

__all__ = ["confusion_matrices"]


def confusion_matrices(
    y_true: np.ndarray,
    y_score: np.ndarray,
    *,
    labels: Optional[List[str]] = None,
    thresholds: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """Binary confusion matrices per label.

    Requires thresholds per label (INPUT_REQUIRED). Labels without a threshold
    are skipped and reported.
    """
    y_true = np.asarray(y_true, dtype=float)
    y_score = np.asarray(y_score, dtype=float)
    if y_true.ndim == 1:
        y_true = y_true.reshape(-1, 1)
        y_score = y_score.reshape(-1, 1)
    thresholds = thresholds or {}
    names = labels or [f"label_{i}" for i in range(y_true.shape[1])]

    matrices: Dict[str, Any] = {}
    skipped: List[str] = []
    for i, name in enumerate(names):
        if name not in thresholds:
            skipped.append(name)
            continue
        y_pred = (y_score[:, i] >= thresholds[name]).astype(int)
        cm = confusion_matrix(y_true[:, i], y_pred)
        matrices[name] = {
            "threshold": float(thresholds[name]),
            "matrix": cm.tolist(),
            "tp": int(cm[1, 1]),
            "fp": int(cm[0, 1]),
            "tn": int(cm[0, 0]),
            "fn": int(cm[1, 0]),
        }
    return {"matrices": matrices, "skipped_no_threshold": skipped}
