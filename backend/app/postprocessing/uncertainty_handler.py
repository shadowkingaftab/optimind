"""Uncertainty and abstention logic.

Applies conservative, configuration-driven rules. Never converts an
unavailable/low-quality input into a successful prediction.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from app.postprocessing.threshold_policy import ThresholdPolicy


@dataclass(frozen=True)
class UncertaintyDecision:
    uncertain: bool = False
    abstain: bool = False
    reason: Optional[str] = None


def decide_uncertainty(
    confidence: Optional[float],
    uncertainty: Optional[float],
    policy: ThresholdPolicy | None = None,
) -> UncertaintyDecision:
    p = policy or ThresholdPolicy()
    if uncertainty is not None and uncertainty > p.uncertainty_threshold:
        return UncertaintyDecision(uncertain=True, reason="uncertainty_high")
    if confidence is not None and confidence < p.abstention_threshold:
        return UncertaintyDecision(abstain=True, reason="confidence_low")
    return UncertaintyDecision()
