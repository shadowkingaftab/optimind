"""Calibration metrics (ECE, MCE, Brier, reliability curve)."""

from __future__ import annotations

from typing import List, Tuple

import numpy as np

__all__ = [
    "expected_calibration_error",
    "maximum_calibration_error",
    "brier_score",
    "reliability_curve",
]


def reliability_curve(
    y_true: np.ndarray, y_prob: np.ndarray, *, n_bins: int = 10
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return (bin_confidence, bin_accuracy, bin_count)."""
    y_true = np.asarray(y_true, dtype=float).ravel()
    y_prob = np.asarray(y_prob, dtype=float).ravel()
    bins = np.linspace(0.0, 1.0, n_bins + 1)
    idx = np.clip(np.digitize(y_prob, bins[1:-1]), 0, n_bins - 1)
    conf = np.zeros(n_bins)
    acc = np.zeros(n_bins)
    count = np.zeros(n_bins, dtype=int)
    for b in range(n_bins):
        mask = idx == b
        count[b] = int(mask.sum())
        if count[b] > 0:
            conf[b] = float(y_prob[mask].mean())
            acc[b] = float(y_true[mask].mean())
    return conf, acc, count


def expected_calibration_error(
    y_true: np.ndarray, y_prob: np.ndarray, *, n_bins: int = 10
) -> float:
    conf, acc, count = reliability_curve(y_true, y_prob, n_bins=n_bins)
    total = count.sum()
    if total == 0:
        return float("nan")
    weights = count / total
    return float((weights * np.abs(acc - conf)).sum())


def maximum_calibration_error(
    y_true: np.ndarray, y_prob: np.ndarray, *, n_bins: int = 10
) -> float:
    conf, acc, count = reliability_curve(y_true, y_prob, n_bins=n_bins)
    mask = count > 0
    if not mask.any():
        return float("nan")
    return float(np.abs(acc[mask] - conf[mask]).max())


def brier_score(y_true: np.ndarray, y_prob: np.ndarray) -> float:
    y_true = np.asarray(y_true, dtype=float).ravel()
    y_prob = np.asarray(y_prob, dtype=float).ravel()
    if y_true.size == 0:
        return float("nan")
    return float(((y_prob - y_true) ** 2).mean())
