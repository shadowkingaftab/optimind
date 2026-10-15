"""Image upload endpoints.

Accepts multipart image uploads, validates and sanitizes them, and returns a
record reference plus a structural quality summary. The stored object key is
not exposed.
"""

from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.api.dependencies import UploadServiceDep
from app.authentication.current_user import CurrentUserDep
from app.authorization.access_control import require_permission
from app.core.permissions import UPLOADS_CREATE
from app.models.eye_image import EyeSide
from app.schemas.image_quality import ImageQualitySummary
from app.schemas.upload import UploadResponse

router = APIRouter(prefix="/uploads", tags=["Uploads"])


@router.post(
    "",
    response_model=UploadResponse,
    status_code=201,
    summary="Upload an eye image",
    dependencies=[Depends(require_permission(UPLOADS_CREATE))],
)
async def create_upload(
    service: UploadServiceDep,
    actor: CurrentUserDep,
    patient_id: uuid.UUID = Form(...),
    eye_side: str = Form(default="unknown"),
    file: UploadFile = File(...),
) -> UploadResponse:
    data = await file.read()
    try:
        side = EyeSide(eye_side.strip().lower())
    except ValueError:
        side = EyeSide.UNKNOWN

    result = await service.create_upload(
        patient_id=patient_id,
        data=data,
        filename=file.filename,
        content_type=file.content_type,
        eye_side=side,
        actor=actor,
    )
    quality = result.quality
    return UploadResponse(
        image_id=result.image.id,
        patient_id=result.image.patient_id,
        media_type=result.image.media_type,
        width=result.image.width,
        height=result.image.height,
        byte_size=result.image.byte_size,
        quality_status=str(result.image.quality_status),
        quality=ImageQualitySummary(
            acceptable=quality.acceptable,
            score=quality.score,
            issues=quality.issues,
            metrics=quality.metrics,
        ),
        created_at=result.image.created_at,
    )
