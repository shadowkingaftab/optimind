"""Classification metrics (accuracy, F1, confusion matrix, report)."""

from __future__ import annotations

from typing import Dict, Optional

import numpy as np

from eyedx_ml.metrics.auroc import roc_auc
from eyedx_ml.metrics.precision_recall import average_precision, precision, recall
from eyedx_ml.metrics.sensitivity import sensitivity
from eyedx_ml.metrics.specificity import specificity

__all__ = [
    "confusion_matrix",
    "accuracy",
    "f1_score",
    "classification_metrics",
]


def confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
    y_true = np.asarray(y_true).astype(int).ravel()
    y_pred = np.asarray(y_pred).astype(int).ravel()
    return np.array(
        [
            [int(((y_true == 0) & (y_pred == 0)).sum()), int(((y_true == 0) & (y_pred == 1)).sum())],
            [int(((y_true == 1) & (y_pred == 0)).sum()), int(((y_true == 1) & (y_pred == 1)).sum())],
        ],
        dtype=int,
    )


def accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    y_true = np.asarray(y_true).ravel()
    y_pred = np.asarray(y_pred).ravel()
    if y_true.size == 0:
        return float("nan")
    return float((y_true == y_pred).mean())


def f1_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    cm = confusion_matrix(y_true, y_pred)
    tp, fp, fn = cm[1, 1], cm[0, 1], cm[1, 0]
    p = precision(tp, fp)
    r = recall(tp, fn)
    return float(2 * p * r / (p + r)) if (p + r) > 0 else 0.0


def classification_metrics(
    y_true: np.ndarray,
    y_score: np.ndarray,
    *,
    threshold: Optional[float] = None,
) -> Dict[str, Optional[float]]:
    """Binary classification metrics. ``threshold`` is INPUT_REQUIRED for
    thresholded metrics; when omitted only threshold-free metrics are returned.
    """
    y_true = np.asarray(y_true, dtype=float).ravel()
    y_score = np.asarray(y_score, dtype=float).ravel()
    result: Dict[str, Optional[float]] = {
        "auroc": roc_auc(y_true, y_score),
        "average_precision": average_precision(y_true, y_score),
    }
    if threshold is not None:
        y_pred = (y_score >= threshold).astype(int)
        cm = confusion_matrix(y_true, y_pred)
        result.update(
            {
                "threshold": float(threshold),
                "accuracy": accuracy(y_true, y_pred),
                "sensitivity": sensitivity(y_true, y_pred),
                "specificity": specificity(y_true, y_pred),
                "f1": f1_score(y_true, y_pred),
                "tp": int(cm[1, 1]),
                "fp": int(cm[0, 1]),
                "tn": int(cm[0, 0]),
                "fn": int(cm[1, 0]),
            }
        )
    return result
