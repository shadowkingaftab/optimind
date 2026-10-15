"""Upload schemas.

The storage key is intentionally not exposed: clients reference uploaded
images by their record id only.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.schemas.image_quality import ImageQualitySummary


class UploadResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    image_id: uuid.UUID
    patient_id: uuid.UUID
    media_type: str
    width: Optional[int] = None
    height: Optional[int] = None
    byte_size: Optional[int] = None
    quality_status: str
    quality: ImageQualitySummary
    created_at: datetime
