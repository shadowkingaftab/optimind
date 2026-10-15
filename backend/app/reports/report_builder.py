"""Report document construction.

Builds a structured, non-diagnostic document from a persisted prediction.
Only values already stored on the prediction are used; nothing is inferred or
fabricated.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from app.models.prediction import Prediction
from app.reports.report_constants import (
    DISCLAIMER_LINE,
    NOTICE_TEXT,
    REPORT_TITLE,
)
from app.utils.datetime import ensure_utc, utcnow


@dataclass(frozen=True)
class ReportCondition:
    label: str
    score: Optional[float]
    risk_level: Optional[str]


@dataclass(frozen=True)
class ReportDocument:
    title: str
    generated_at: datetime
    patient_code: Optional[str]
    status: str
    risk_level: Optional[str]
    outcome_label: Optional[str]
    confidence: Optional[float]
    model_version: Optional[str]
    conditions: list[ReportCondition] = field(default_factory=list)
    notice: str = NOTICE_TEXT
    disclaimer: str = DISCLAIMER_LINE
    metadata: dict[str, Any] = field(default_factory=dict)


def build_report_document(
    prediction: Prediction,
    *,
    patient_code: Optional[str] = None,
    generated_at: Optional[datetime] = None,
) -> ReportDocument:
    """Create a :class:`ReportDocument` from a prediction."""
    conditions = [
        ReportCondition(
            label=item.condition_label or item.condition_code,
            score=item.score,
            risk_level=str(item.risk_level) if item.risk_level else None,
        )
        for item in getattr(prediction, "items", []) or []
    ]
    return ReportDocument(
        title=REPORT_TITLE,
        generated_at=ensure_utc(generated_at) or utcnow(),
        patient_code=patient_code,
        status=str(prediction.status),
        risk_level=str(prediction.risk_level) if prediction.risk_level else None,
        outcome_label=prediction.outcome_label,
        confidence=prediction.confidence,
        model_version=prediction.model_version_label,
        conditions=conditions,
        metadata={"prediction_id": str(prediction.id)},
    )
