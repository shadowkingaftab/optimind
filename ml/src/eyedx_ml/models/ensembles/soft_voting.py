"""Soft-voting ensemble."""

from __future__ import annotations

from typing import Sequence

import numpy as np

from eyedx_ml.errors import NotConfiguredError

__all__ = ["soft_vote", "SoftVotingEnsemble"]


def _stack(probabilities: Sequence[np.ndarray]) -> np.ndarray:
    if not probabilities:
        raise NotConfiguredError("soft voting requires at least one member")
    arrays = [np.asarray(p, dtype=float) for p in probabilities]
    shape = arrays[0].shape
    for a in arrays:
        if a.shape != shape:
            raise NotConfiguredError("ensemble members must share output shape")
    return np.stack(arrays, axis=0)


def soft_vote(probabilities: Sequence[np.ndarray]) -> np.ndarray:
    """Average member probabilities element-wise."""
    return _stack(probabilities).mean(axis=0)


class SoftVotingEnsemble:
    """Combines member callables using unweighted mean of probabilities."""

    def __init__(self, members: Sequence = None):
        self.members = list(members or [])

    def add(self, member) -> None:
        self.members.append(member)

    def predict_proba(self, inputs) -> np.ndarray:
        if not self.members:
            raise NotConfiguredError("no ensemble members configured")
        outputs = []
        for member in self.members:
            outputs.append(np.asarray(member(inputs), dtype=float))
        return soft_vote(outputs)
