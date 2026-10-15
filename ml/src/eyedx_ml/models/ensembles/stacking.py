"""Stacking ensemble with a meta-learner."""

from __future__ import annotations

from typing import Optional, Sequence

import numpy as np

from eyedx_ml.errors import DependencyError, NotConfiguredError

__all__ = ["StackingEnsemble"]


class StackingEnsemble:
    """Trains a meta-learner on out-of-fold member predictions.

    Base members produce probability vectors; their concatenation feeds a
    meta-learner (default logistic regression). Out-of-fold predictions must
    come from the train split to avoid leakage.
    """

    def __init__(self, members: Sequence = None, meta_learner=None):
        self.members = list(members or [])
        self.meta_learner = meta_learner

    def _default_meta(self):
        try:
            from sklearn.linear_model import LogisticRegression
        except Exception as exc:  # pragma: no cover - optional dependency
            raise DependencyError(
                "scikit-learn is required for stacking (pip install scikit-learn)"
            ) from exc
        return LogisticRegression(max_iter=1000)

    def fit(self, oof_predictions: Sequence[np.ndarray], targets: np.ndarray):
        """Fit the meta-learner on out-of-fold predictions.

        ``oof_predictions`` is a sequence of (n_samples, n_outputs) arrays.
        """
        if not oof_predictions:
            raise NotConfiguredError("stacking requires out-of-fold predictions")
        features = np.concatenate(
            [np.asarray(p, dtype=float) for p in oof_predictions], axis=1
        )
        self.meta_learner = self.meta_learner or self._default_meta()
        self.meta_learner.fit(features, np.asarray(targets))
        return self

    def predict_proba(self, member_predictions: Sequence[np.ndarray]) -> np.ndarray:
        if self.meta_learner is None:
            raise NotConfiguredError("meta-learner is not fitted")
        features = np.concatenate(
            [np.asarray(p, dtype=float) for p in member_predictions], axis=1
        )
        if hasattr(self.meta_learner, "predict_proba"):
            return self.meta_learner.predict_proba(features)
        return self.meta_learner.predict(features)
