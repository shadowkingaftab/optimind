"""Threshold policy (configuration-driven).

Values marked INPUT_REQUIRED must be provided via configuration. Where not
provided, conservative defaults are used that do not fabricate clinical
performance. The absence of thresholds must be handled explicitly downstream.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ThresholdPolicy:
    """Structurally-configurable thresholds (non-clinical default values).

    These are input-required to be tuned per approved model and clinical
    acceptance criteria. The defaults here are safe placeholders only.
    """

    min_brightness: float = 0.2
    max_blur_score: float = 0.3
    min_resolution: int = 256
    max_aspect_ratio_deviation: float = 0.3
    uncertainty_threshold: float = 0.6
    abstention_threshold: float = 0.5
    confidence_threshold: float = 0.5
    min_confidence_for_success: float = 0.5

    @classmethod
    def from_dict(cls, data: dict) -> "ThresholdPolicy":
        if not isinstance(data, dict):
            return cls()
        return cls(
            min_brightness=float(data.get("min_brightness", cls.min_brightness)),
            max_blur_score=float(data.get("max_blur_score", cls.max_blur_score)),
            min_resolution=int(data.get("min_resolution", cls.min_resolution)),
            max_aspect_ratio_deviation=float(
                data.get(
                    "max_aspect_ratio_deviation",
                    cls.max_aspect_ratio_deviation,
                )
            ),
            uncertainty_threshold=float(
                data.get("uncertainty_threshold", cls.uncertainty_threshold)
            ),
            abstention_threshold=float(
                data.get("abstention_threshold", cls.abstention_threshold)
            ),
            confidence_threshold=float(
                data.get("confidence_threshold", cls.confidence_threshold)
            ),
            min_confidence_for_success=float(
                data.get(
                    "min_confidence_for_success",
                    cls.min_confidence_for_success,
                )
            ),
        )
