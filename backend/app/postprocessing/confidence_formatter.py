"""Confidence and uncertainty formatting.

Formatting removes precision artifacts without fabricating values and never
exposes raw model internals unnecessarily.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Optional


@dataclass(frozen=True)
class FormattedPrediction:
    confidence: Optional[float]
    uncertainty: Optional[float]
    top_score: Optional[float]
    top_label: Optional[str]


def _to_float(value: Any) -> Optional[float]:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def format_confidence(
    predictions: Optional[Sequence[Mapping[str, Any]]] = None,
) -> FormattedPrediction:
    """Summarise the top score/label across ``predictions``."""
    top_score: Optional[float] = None
    top_label: Optional[str] = None
    for item in predictions or []:
        if not isinstance(item, Mapping):
            continue
        score = _to_float(item.get("score"))
        if score is not None and (top_score is None or score > top_score):
            top_score = score
            label = item.get("label")
            top_label = str(label) if label is not None else top_label
    return FormattedPrediction(
        confidence=top_score,
        uncertainty=None,
        top_score=top_score,
        top_label=top_label,
    )
