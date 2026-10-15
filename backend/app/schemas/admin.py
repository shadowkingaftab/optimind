"""Administrative schemas."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class AuditLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    action: str
    actor_user_id: Optional[uuid.UUID] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    status: str
    request_id: Optional[str] = None
    created_at: datetime


class SystemStatistics(BaseModel):
    """Aggregate, non-clinical operational statistics."""

    total_predictions: int = 0
    predictions_by_status: dict[str, int] = {}
    total_patients: int = 0
    total_uploads: int = 0
    active_model_version: Optional[str] = None
