"""Precision, recall and average precision (numpy)."""

from __future__ import annotations

from typing import Optional

import numpy as np

__all__ = ["precision", "recall", "average_precision"]


def precision(tp: float, fp: float) -> float:
    denom = tp + fp
    return float(tp / denom) if denom > 0 else 0.0


def recall(tp: float, fn: float) -> float:
    denom = tp + fn
    return float(tp / denom) if denom > 0 else 0.0


def average_precision(y_true: np.ndarray, y_score: np.ndarray) -> Optional[float]:
    """Average precision (area under precision-recall curve) via step integral."""
    y_true = np.asarray(y_true, dtype=float).ravel()
    y_score = np.asarray(y_score, dtype=float).ravel()
    if y_true.size == 0:
        return None
    n_pos = float((y_true == 1).sum())
    if n_pos == 0:
        return None
    order = np.argsort(-y_score)
    y_true = y_true[order]
    precision_at = np.cumsum(y_true) / (np.arange(y_true.size) + 1)
    return float((precision_at * y_true).sum() / n_pos)
