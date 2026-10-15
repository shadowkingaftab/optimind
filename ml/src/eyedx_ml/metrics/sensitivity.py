"""Sensitivity (recall) metrics."""

from __future__ import annotations

from typing import Optional

import numpy as np

__all__ = ["sensitivity", "sensitivity_at_threshold"]


def sensitivity(y_true: np.ndarray, y_pred: np.ndarray) -> Optional[float]:
    y_true = np.asarray(y_true, dtype=float).ravel()
    y_pred = np.asarray(y_pred, dtype=float).ravel()
    positives = y_true == 1
    n_pos = int(positives.sum())
    if n_pos == 0:
        return None
    return float((y_pred[positives] == 1).sum() / n_pos)


def sensitivity_at_threshold(
    y_true: np.ndarray, y_score: np.ndarray, threshold: float
) -> Optional[float]:
    y_score = np.asarray(y_score, dtype=float).ravel()
    return sensitivity(y_true, (y_score >= threshold).astype(int))
