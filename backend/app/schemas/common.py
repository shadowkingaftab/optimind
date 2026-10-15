"""Common schema building blocks shared across the API."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ORMModel(BaseModel):
    """Base for schemas populated from ORM objects."""

    model_config = ConfigDict(from_attributes=True)


class IdentifiedModel(ORMModel):
    """An entity exposing a UUID primary key and audit timestamps."""

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class MessageResponse(BaseModel):
    """Generic single-message response."""

    message: str


class TimestampedResponse(ORMModel):
    """A response carrying only identity and timestamps."""

    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime] = None


class HealthStatus(BaseModel):
    """Liveness/readiness payload for infrastructure probes."""

    status: str = Field(default="ok", description="ok | degraded | unavailable")
    version: str
    database: str = Field(
        default="unknown",
        description="Database connectivity status: ok | unavailable | unknown",
    )
