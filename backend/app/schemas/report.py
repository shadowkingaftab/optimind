"""Report schemas."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ReportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    patient_id: uuid.UUID
    prediction_id: Optional[uuid.UUID] = None
    status: str
    media_type: Optional[str] = None
    byte_size: Optional[int] = None
    generated_at: Optional[datetime] = None
    created_at: datetime


class ReportPreview(BaseModel):
    """A plain-text preview of a report."""

    prediction_id: uuid.UUID
    text: str


class ReportGenerateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    prediction_id: uuid.UUID = Field(description="Prediction to report on.")
