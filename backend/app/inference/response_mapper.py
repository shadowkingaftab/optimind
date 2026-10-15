"""Map and validate model-service responses.

Enforces the shared contract. A response missing required fields or carrying
an unknown status is rejected with ``InferenceContractError`` rather than
being coerced into a success.
"""

from __future__ import annotations

from typing import Any, Mapping

from app.core.constants import SCREENING_LIMITATION_NOTICE
from app.exceptions.inference import InferenceContractError
from app.inference.inference_contract import (
    REQUIRED_RESPONSE_FIELDS,
    VALID_STATUSES,
    InferenceResult,
)


def map_response(payload: Mapping[str, Any]) -> InferenceResult:
    """Convert a raw response mapping into an :class:`InferenceResult`."""
    if not isinstance(payload, Mapping):
        raise InferenceContractError("Response payload is not an object.")

    missing = [field for field in REQUIRED_RESPONSE_FIELDS if field not in payload]
    if missing:
        raise InferenceContractError(
            "Response missing required fields: " + ", ".join(missing)
        )

    status = str(payload["status"])
    if status not in VALID_STATUSES:
        raise InferenceContractError(f"Unknown prediction status: {status!r}.")

    try:
        processing_time_ms = int(payload["processing_time_ms"])
    except (TypeError, ValueError) as exc:
        raise InferenceContractError("processing_time_ms is not an integer.") from exc

    predictions = payload.get("predictions") or []
    if not isinstance(predictions, list):
        raise InferenceContractError("predictions must be an array.")
    normalized_predictions = []
    for item in predictions:
        if not isinstance(item, Mapping) or "label" not in item or "score" not in item:
            raise InferenceContractError(
                "Each prediction requires 'label' and 'score'."
            )
        normalized_predictions.append(
            {"label": str(item["label"]), "score": float(item["score"])}
        )

    return InferenceResult(
        request_id=str(payload["request_id"]),
        status=status,
        model_id=str(payload["model_id"]),
        model_version=str(payload["model_version"]),
        processing_time_ms=max(0, processing_time_ms),
        predictions=normalized_predictions,
        uncertainty=_as_optional_dict(payload.get("uncertainty")),
        explanation=_as_optional_dict(payload.get("explanation")),
        quality_checks=_as_optional_dict(payload.get("quality_checks")),
        abstention_reason=_as_optional_str(payload.get("abstention_reason")),
        failure_reason=_as_optional_str(payload.get("failure_reason")),
        limitation_notice=_as_optional_str(payload.get("limitation_notice"))
        or SCREENING_LIMITATION_NOTICE,
    )


def _as_optional_dict(value: Any) -> dict[str, Any] | None:
    return dict(value) if isinstance(value, Mapping) else None


def _as_optional_str(value: Any) -> str | None:
    return str(value) if value is not None else None
