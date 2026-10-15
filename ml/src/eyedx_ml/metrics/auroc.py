"""Area under the ROC curve (numpy implementation).

Implemented directly so metrics never require a heavy optional dependency. Handles
the single-label case and per-label evaluation for multi-label problems.
"""

from __future__ import annotations

from typing import List, Optional

import numpy as np

__all__ = ["roc_auc", "roc_auc_per_label"]


def roc_auc(y_true: np.ndarray, y_score: np.ndarray) -> Optional[float]:
    """Return ROC AUC, or ``None`` when only one class is present.

    Uses the rank-based (Mann-Whitney U) formulation with tie handling.
    """
    y_true = np.asarray(y_true, dtype=float).ravel()
    y_score = np.asarray(y_score, dtype=float).ravel()
    if y_true.shape != y_score.shape:
        raise ValueError("y_true and y_score must have the same length")
    if y_true.size == 0:
        return None
    pos = y_true == 1
    n_pos = int(pos.sum())
    n_neg = int((~pos).sum())
    if n_pos == 0 or n_neg == 0:
        return None
    order = np.argsort(y_score)
    ranks = np.empty_like(order, dtype=float)
    ranks[order] = np.arange(1, y_score.size + 1, dtype=float)
    # average ranks for ties
    sorted_scores = y_score[order]
    i = 0
    while i < sorted_scores.size:
        j = i
        while j + 1 < sorted_scores.size and sorted_scores[j + 1] == sorted_scores[i]:
            j += 1
        if j > i:
            avg = (i + j + 2) / 2.0  # ranks are 1-based
            for k in range(i, j + 1):
                ranks[order[k]] = avg
        i = j + 1
    rank_sum = ranks[pos].sum()
    auc = (rank_sum - n_pos * (n_pos + 1) / 2.0) / (n_pos * n_neg)
    return float(auc)


def roc_auc_per_label(y_true: np.ndarray, y_score: np.ndarray) -> List[Optional[float]]:
    """Per-column ROC AUC for a 2D (n_samples, n_labels) array."""
    y_true = np.asarray(y_true)
    y_score = np.asarray(y_score)
    if y_true.ndim != 2:
        raise ValueError("expected 2D arrays for per-label scoring")
    return [roc_auc(y_true[:, i], y_score[:, i]) for i in range(y_true.shape[1])]
