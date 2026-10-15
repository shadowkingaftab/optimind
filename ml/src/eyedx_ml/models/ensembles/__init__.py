"""Ensemble strategies."""

from __future__ import annotations

from .soft_voting import SoftVotingEnsemble, soft_vote
from .stacking import StackingEnsemble
from .weighted_voting import WeightedVotingEnsemble, weighted_vote

__all__ = [
    "SoftVotingEnsemble",
    "soft_vote",
    "WeightedVotingEnsemble",
    "weighted_vote",
    "StackingEnsemble",
]
