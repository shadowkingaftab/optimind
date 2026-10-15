"""Prediction endpoints.

``POST /predictions`` accepts a base64 image and a consent reference. The
image is safely ingested, then screened. A low-quality image never yields a
disease result; failed or uncertain outcomes are reported honestly.
"""

from __future__ import annotations

import base64
import binascii
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import (
    ConsentServiceDep,
    PageParamsDep,
    PredictionServiceDep,
    UploadServiceDep,
)
from app.authentication.current_user import CurrentUserDep
from app.core.permissions import PREDICTIONS_CREATE, PREDICTIONS_READ
from app.core.request_context import get_request_id
from app.authorization.access_control import require_permission
from app.exceptions.authorization import ConsentExpiredError
from app.exceptions.validation import RequestValidationError
from app.schemas.pagination import Page
from app.schemas.prediction import (
    PredictionRead,
    PredictionRequest,
    PredictionResponse,
)

router = APIRouter(prefix="/predictions", tags=["Predictions"])


def _decode_image(image: str, image_format: Optional[str]) -> tuple[bytes, str, str]:
    try:
        data = base64.b64decode(image, validate=True)
    except (ValueError, binascii.Error) as exc:
        raise RequestValidationError("The image is not valid base64 data.") from exc
    if not data:
        raise RequestValidationError("The image payload is empty.")
    if image_format == "png":
        return data, "upload.png", "image/png"
    return data, "upload.jpg", "image/jpeg"


@router.post(
    "",
    response_model=PredictionResponse,
    summary="Run a screening prediction",
    dependencies=[Depends(require_permission(PREDICTIONS_CREATE))],
)
async def create_prediction(
    payload: PredictionRequest,
    service: PredictionServiceDep,
    uploads: UploadServiceDep,
    consents: ConsentServiceDep,
    actor: CurrentUserDep,
) -> PredictionResponse:
    try:
        consent_id = uuid.UUID(payload.consent_id)
    except (ValueError, TypeError) as exc:
        raise RequestValidationError("consent_id must be a valid identifier.") from exc

    consent = await consents.get(consent_id)
    if not consent.is_active:
        raise ConsentExpiredError()
    patient_id = consent.patient_id

    data, filename, content_type = _decode_image(payload.image, payload.image_format)
    upload = await uploads.create_upload(
        patient_id=patient_id,
        data=data,
        filename=filename,
        content_type=content_type,
        actor=actor,
        enforce_consent=False,
    )

    outcome = await service.predict(
        patient_id=patient_id,
        eye_image_id=upload.image.id,
        actor=actor,
        request_id=payload.request_id or get_request_id(),
    )
    return PredictionResponse(**outcome.response)


@router.get(
    "/{prediction_id}",
    response_model=PredictionRead,
    summary="Get a prediction",
    dependencies=[Depends(require_permission(PREDICTIONS_READ))],
)
async def get_prediction(
    prediction_id: uuid.UUID, service: PredictionServiceDep
) -> PredictionRead:
    prediction = await service.get(prediction_id)
    return PredictionRead.model_validate(prediction)


@router.get(
    "",
    response_model=Page[PredictionRead],
    summary="List predictions for a patient",
    dependencies=[Depends(require_permission(PREDICTIONS_READ))],
)
async def list_predictions(
    service: PredictionServiceDep,
    params: PageParamsDep,
    patient_id: uuid.UUID = Query(...),
) -> Page[PredictionRead]:
    items = await service.list_for_patient(
        patient_id, limit=params.limit, offset=params.offset
    )
    total = await service.count_for_patient(patient_id)
    return Page.create(
        [PredictionRead.model_validate(item) for item in items],
        total=total,
        page=params.page,
        page_size=params.page_size,
    )
