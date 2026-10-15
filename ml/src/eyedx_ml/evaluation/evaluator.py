"""Model evaluation.

Computes per-label and aggregate metrics from prediction scores. Thresholds are
supplied by the caller (approved operating points); when omitted only
threshold-free metrics are produced. No metric is ever fabricated.
"""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional, Sequence

import numpy as np

from eyedx_ml.metrics.auroc import roc_auc
from eyedx_ml.metrics.bootstrap_confidence_intervals import bootstrap_ci
from eyedx_ml.metrics.calibration import (
    brier_score,
    expected_calibration_error,
)
from eyedx_ml.metrics.classification import classification_metrics
from eyedx_ml.metrics.precision_recall import average_precision

__all__ = ["compute_label_metrics", "Evaluator"]


def _as_2d(y: np.ndarray) -> np.ndarray:
    y = np.asarray(y, dtype=float)
    if y.ndim == 1:
        y = y.reshape(-1, 1)
    return y


def compute_label_metrics(
    y_true: np.ndarray,
    y_score: np.ndarray,
    *,
    threshold: Optional[float] = None,
    bootstrap: bool = False,
    n_resamples: int = 1000,
    confidence_level: float = 0.95,
    seed: int = 42,
) -> Dict[str, Any]:
    """Metrics for a single binary label."""
    y_true = np.asarray(y_true, dtype=float).ravel()
    y_score = np.asarray(y_score, dtype=float).ravel()
    metrics = classification_metrics(y_true, y_score, threshold=threshold)
    metrics["brier_score"] = brier_score(y_true, y_score)
    metrics["ece"] = expected_calibration_error(y_true, y_score)
    if bootstrap:
        metrics["auroc_ci"] = bootstrap_ci(
            roc_auc,
            y_true,
            y_score,
            n_resamples=n_resamples,
            confidence_level=confidence_level,
            seed=seed,
        )
        metrics["average_precision_ci"] = bootstrap_ci(
            average_precision,
            y_true,
            y_score,
            n_resamples=n_resamples,
            confidence_level=confidence_level,
            seed=seed,
        )
    return metrics


class Evaluator:
    def __init__(
        self,
        labels: Sequence[str],
        *,
        thresholds: Optional[Mapping[str, float]] = None,
        bootstrap: bool = False,
        n_resamples: int = 1000,
        confidence_level: float = 0.95,
        seed: int = 42,
    ) -> None:
        self.labels = list(labels)
        self.thresholds = dict(thresholds or {})
        self.bootstrap = bootstrap
        self.n_resamples = n_resamples
        self.confidence_level = confidence_level
        self.seed = seed

    def evaluate(self, y_true: np.ndarray, y_score: np.ndarray) -> Dict[str, Any]:
        y_true = _as_2d(y_true)
        y_score = _as_2d(y_score)
        if y_true.shape != y_score.shape:
            raise ValueError("y_true and y_score must have the same shape")
        n_labels = y_true.shape[1]
        labels = self.labels or [f"label_{i}" for i in range(n_labels)]
        if len(labels) != n_labels:
            raise ValueError(
                f"expected {n_labels} label names, got {len(labels)}"
            )

        per_label: Dict[str, Any] = {}
        macro_values: Dict[str, List[float]] = {}
        for i, name in enumerate(labels):
            metrics = compute_label_metrics(
                y_true[:, i],
                y_score[:, i],
                threshold=self.thresholds.get(name),
                bootstrap=self.bootstrap,
                n_resamples=self.n_resamples,
                confidence_level=self.confidence_level,
                seed=self.seed,
            )
            per_label[name] = metrics
            for key in ("auroc", "average_precision", "brier_score", "ece", "sensitivity", "specificity", "f1"):
                value = metrics.get(key)
                if isinstance(value, (int, float)) and not np.isnan(value):
                    macro_values.setdefault(key, []).append(float(value))

        macro = {
            key: float(np.mean(vals)) for key, vals in macro_values.items() if vals
        }
        return {
            "n_samples": int(y_true.shape[0]),
            "labels": labels,
            "per_label": per_label,
            "macro": macro,
            "thresholds": self.thresholds,
        }
