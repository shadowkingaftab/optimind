"""Format model outputs into the PredictionResponse contract shape.

The formatter preserves the contract shape and never fabricates clinical
values.
"""

from __future__ import annotations

from typing import Any, Mapping, Optional

from app.core.constants import SCREENING_LIMITATION_NOTICE
from app.models.prediction import PredictionStatus


def build_prediction_response(
    *,
    request_id: str,
    status: PredictionStatus,
    model_id: str,
    model_version: str,
    processing_time_ms: int,
    predictions: Optional[list[dict]] = None,
    uncertainty: Optional[Mapping[str, Any]] = None,
    explanation: Optional[Mapping[str, Any]] = None,
    quality_checks: Optional[Mapping[str, Any]] = None,
    abstention_reason: Optional[str] = None,
    failure_reason: Optional[str] = None,
) -> dict[str, Any]:
    """Build a contract-compatible prediction response body."""
    body: dict[str, Any] = {
        "request_id": request_id,
        "status": status.value if hasattr(status, "value") else str(status),
        "model_id": model_id,
        "model_version": model_version,
        "processing_time_ms": max(0, int(processing_time_ms)),
        "limitation_notice": SCREENING_LIMITATION_NOTICE,
    }
    if predictions:
        body["predictions"] = predictions
    if uncertainty:
        body["uncertainty"] = dict(uncertainty)
    if explanation:
        body["explanation"] = dict(explanation)
    if quality_checks:
        body["quality_checks"] = dict(quality_checks)
    if abstention_reason:
        body["abstention_reason"] = abstention_reason
    if failure_reason:
        body["failure_reason"] = failure_reason
    return body
