"""Prediction schemas.

These mirror the shared contracts
(``prediction-request.schema.json`` / ``prediction-response.schema.json``).
The request accepts a base64 image plus a consent reference; the response
always carries the non-diagnostic limitation notice.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import SCREENING_LIMITATION_NOTICE

PredictionStatusLiteral = Literal[
    "success", "low_quality", "uncertain", "abstained", "failed"
]


class PredictionRequest(BaseModel):
    """Request body for POST /predictions."""

    model_config = ConfigDict(extra="forbid")

    image: str = Field(min_length=1, description="Base64-encoded image bytes.")
    consent_id: str = Field(
        min_length=1, description="Reference to an active consent record."
    )
    image_format: Optional[Literal["jpeg", "png"]] = None
    request_id: Optional[str] = Field(default=None, max_length=64)


class PredictionItemResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    label: str
    score: float


class PredictionResponse(BaseModel):
    """Response body matching the prediction-response contract."""

    model_config = ConfigDict(extra="forbid")

    request_id: str
    status: PredictionStatusLiteral
    model_id: str
    model_version: str
    processing_time_ms: int = Field(ge=0)
    predictions: list[PredictionItemResponse] = Field(default_factory=list)
    uncertainty: Optional[dict[str, Any]] = None
    explanation: Optional[dict[str, Any]] = None
    quality_checks: Optional[dict[str, Any]] = None
    abstention_reason: Optional[str] = None
    failure_reason: Optional[str] = None
    limitation_notice: str = SCREENING_LIMITATION_NOTICE


class PredictionRead(BaseModel):
    """A persisted prediction record."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    patient_id: uuid.UUID
    eye_image_id: Optional[uuid.UUID] = None
    status: PredictionStatusLiteral
    risk_level: Optional[str] = None
    outcome_label: Optional[str] = None
    confidence: Optional[float] = None
    uncertainty: Optional[float] = None
    quality_score: Optional[float] = None
    model_version_label: Optional[str] = None
    latency_ms: Optional[int] = None
    created_at: datetime
