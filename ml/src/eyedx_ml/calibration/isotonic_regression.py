"""Isotonic regression calibration (scikit-learn)."""

from __future__ import annotations

from typing import Optional

import numpy as np

from eyedx_ml.errors import DependencyError, NotConfiguredError

__all__ = ["IsotonicCalibrator"]


class IsotonicCalibrator:
    """Monotonic mapping from scores to calibrated probabilities.

    Fit on the validation split. Not recommended for very small validation sets
    (may overfit); size checks are the caller's responsibility.
    """

    def __init__(self, *, out_of_bounds: str = "clip") -> None:
        self.out_of_bounds = out_of_bounds
        self.model = None

    def fit(self, y_true: np.ndarray, y_prob: np.ndarray) -> "IsotonicCalibrator":
        try:
            from sklearn.isotonic import IsotonicRegression
        except Exception as exc:  # pragma: no cover - optional dependency
            raise DependencyError(
                "scikit-learn is required for isotonic calibration"
            ) from exc
        y_true = np.asarray(y_true, dtype=float).ravel()
        y_prob = np.asarray(y_prob, dtype=float).ravel()
        if y_true.size == 0:
            raise NotConfiguredError("isotonic calibration needs non-empty data")
        self.model = IsotonicRegression(out_of_bounds=self.out_of_bounds)
        self.model.fit(y_prob, y_true)
        return self

    def transform(self, y_prob: np.ndarray) -> np.ndarray:
        if self.model is None:
            raise NotConfiguredError("IsotonicCalibrator is not fitted")
        return self.model.predict(np.asarray(y_prob, dtype=float).ravel())

    @property
    def fitted(self) -> bool:
        return self.model is not None
