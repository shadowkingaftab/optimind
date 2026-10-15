"""Weighted-voting ensemble."""

from __future__ import annotations

from typing import Sequence

import numpy as np

from eyedx_ml.errors import NotConfiguredError

__all__ = ["weighted_vote", "WeightedVotingEnsemble"]


def weighted_vote(
    probabilities: Sequence[np.ndarray], weights: Sequence[float]
) -> np.ndarray:
    """Weighted average of member probabilities.

    Weights are INPUT_REQUIRED: they must derive from validation performance and
    be documented, not guessed.
    """
    if not probabilities:
        raise NotConfiguredError("weighted voting requires at least one member")
    if len(probabilities) != len(weights):
        raise NotConfiguredError("weights length must match number of members")
    arrays = np.stack([np.asarray(p, dtype=float) for p in probabilities], axis=0)
    w = np.asarray(weights, dtype=float)
    if np.isclose(w.sum(), 0.0):
        raise NotConfiguredError("ensemble weights must not sum to zero")
    w = w / w.sum()
    reshaped = w.reshape((-1,) + (1,) * (arrays.ndim - 1))
    return (arrays * reshaped).sum(axis=0)


class WeightedVotingEnsemble:
    def __init__(self, members: Sequence = None, weights: Sequence[float] = None):
        self.members = list(members or [])
        self.weights = list(weights or [])

    def predict_proba(self, inputs) -> np.ndarray:
        if not self.members:
            raise NotConfiguredError("no ensemble members configured")
        if len(self.weights) != len(self.members):
            raise NotConfiguredError(
                "weights are INPUT_REQUIRED and must match the number of members"
            )
        outputs = [np.asarray(m(inputs), dtype=float) for m in self.members]
        return weighted_vote(outputs, self.weights)
