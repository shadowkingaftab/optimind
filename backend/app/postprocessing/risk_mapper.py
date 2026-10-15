"""Risk level mapping.

Maps numeric scores to risk level categories. Thresholds are configuration
inputs and must not be treated as validated clinical cutoffs by default.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.models.prediction import RiskLevel


@dataclass(frozen=True)
class RiskThresholds:
    low_threshold: float = 0.3
    moderate_threshold: float = 0.6

    def map(self, score: float | None) -> RiskLevel:
        if score is None:
            return RiskLevel.UNKNOWN
        try:
            s = float(score)
        except (TypeError, ValueError):
            return RiskLevel.UNKNOWN
        if s < 0.0:
            s = 0.0
        if s > 1.0:
            s = 1.0
        if s >= self.moderate_threshold:
            return RiskLevel.HIGH
        if s >= self.low_threshold:
            return RiskLevel.MODERATE
        return RiskLevel.LOW


def map_score_to_risk(score: float | None, thresholds: RiskThresholds | None = None) -> RiskLevel:
    return (thresholds or RiskThresholds()).map(score)
