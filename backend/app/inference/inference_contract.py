"""Internal inference contracts.

These structures are the backend's working representation of the model
service request/response. Their field names match
``contracts/json-schemas/prediction-response.schema.json`` so mapping is
explicit and verifiable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from app.core.constants import PREDICTION_STATUSES


@dataclass(frozen=True)
class InferenceRequest:
    """Payload sent to the model service ``/predict`` endpoint."""

    image_base64: str
    consent_id: str
    image_format: Optional[str] = None
    request_id: Optional[str] = None

    def to_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "image": self.image_base64,
            "consent_id": self.consent_id,
        }
        if self.image_format:
            payload["image_format"] = self.image_format
        if self.request_id:
            payload["request_id"] = self.request_id
        return payload


@dataclass(frozen=True)
class InferenceResult:
    """Normalised result returned by an inference client."""

    request_id: str
    status: str
    model_id: str
    model_version: str
    processing_time_ms: int
    predictions: list[dict[str, Any]] = field(default_factory=list)
    uncertainty: Optional[dict[str, Any]] = None
    explanation: Optional[dict[str, Any]] = None
    quality_checks: Optional[dict[str, Any]] = None
    abstention_reason: Optional[str] = None
    failure_reason: Optional[str] = None
    limitation_notice: Optional[str] = None

    @property
    def is_success(self) -> bool:
        return self.status == "success"

    def to_response_dict(self) -> dict[str, Any]:
        body: dict[str, Any] = {
            "request_id": self.request_id,
            "status": self.status,
            "model_id": self.model_id,
            "model_version": self.model_version,
            "processing_time_ms": self.processing_time_ms,
        }
        if self.predictions:
            body["predictions"] = [dict(p) for p in self.predictions]
        if self.uncertainty:
            body["uncertainty"] = dict(self.uncertainty)
        if self.explanation:
            body["explanation"] = dict(self.explanation)
        if self.quality_checks:
            body["quality_checks"] = dict(self.quality_checks)
        if self.abstention_reason:
            body["abstention_reason"] = self.abstention_reason
        if self.failure_reason:
            body["failure_reason"] = self.failure_reason
        if self.limitation_notice:
            body["limitation_notice"] = self.limitation_notice
        return body


REQUIRED_RESPONSE_FIELDS = (
    "request_id",
    "status",
    "model_id",
    "model_version",
    "processing_time_ms",
)

VALID_STATUSES = PREDICTION_STATUSES
