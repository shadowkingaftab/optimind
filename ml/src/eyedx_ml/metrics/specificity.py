"""Specificity metrics."""

from __future__ import annotations

from typing import Optional

import numpy as np

__all__ = ["specificity", "specificity_at_threshold"]


def specificity(y_true: np.ndarray, y_pred: np.ndarray) -> Optional[float]:
    y_true = np.asarray(y_true, dtype=float).ravel()
    y_pred = np.asarray(y_pred, dtype=float).ravel()
    negatives = y_true == 0
    n_neg = int(negatives.sum())
    if n_neg == 0:
        return None
    return float((y_pred[negatives] == 0).sum() / n_neg)


def specificity_at_threshold(
    y_true: np.ndarray, y_score: np.ndarray, threshold: float
) -> Optional[float]:
    y_score = np.asarray(y_score, dtype=float).ravel()
    return specificity(y_true, (y_score >= threshold).astype(int))
