"""Format inference results to the prediction-response contract.

Only fields allowed by ``prediction-response.schema.json`` are emitted.
"""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional, Sequence

__all__ = ["LIMITATION_NOTICE", "format_predictions", "format_response"]

LIMITATION_NOTICE = (
    "Screening assistance only. This is not a diagnosis and must be reviewed by a "
    "qualified clinician."
)

VALID_STATUS = {"success", "low_quality", "uncertain", "abstained", "failed"}


def format_predictions(
    labels: Sequence[str], scores: Sequence[float]
) -> List[Dict[str, Any]]:
    if len(labels) != len(scores):
        raise ValueError("labels and scores must have the same length")
    out = []
    for label, score in zip(labels, scores):
        value = float(min(1.0, max(0.0, score)))
        out.append({"label": str(label), "score": value})
    return out


def format_response(
    *,
    request_id: str,
    status: str,
    model_id: str,
    model_version: str,
    processing_time_ms: int,
    predictions: Optional[Sequence[Mapping[str, Any]]] = None,
    uncertainty: Optional[Mapping[str, Any]] = None,
    explanation: Optional[Mapping[str, Any]] = None,
    quality_checks: Optional[Mapping[str, Any]] = None,
    abstention_reason: Optional[str] = None,
    failure_reason: Optional[str] = None,
    include_limitation_notice: bool = True,
) -> Dict[str, Any]:
    if status not in VALID_STATUS:
        raise ValueError(f"invalid status: {status}")
    response: Dict[str, Any] = {
        "request_id": request_id,
        "status": status,
        "model_id": model_id,
        "model_version": model_version,
        "processing_time_ms": int(max(0, processing_time_ms)),
    }
    if predictions is not None:
        response["predictions"] = [dict(p) for p in predictions]
    if uncertainty is not None:
        response["uncertainty"] = dict(uncertainty)
    if explanation is not None:
        response["explanation"] = dict(explanation)
    if quality_checks is not None:
        response["quality_checks"] = dict(quality_checks)
    if abstention_reason is not None:
        response["abstention_reason"] = abstention_reason
    if failure_reason is not None:
        response["failure_reason"] = failure_reason
    if include_limitation_notice:
        response["limitation_notice"] = LIMITATION_NOTICE
    return response
