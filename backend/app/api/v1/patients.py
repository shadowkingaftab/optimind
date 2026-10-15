"""Patient and consent endpoints.

Patients are pseudonymous. Consent is explicit: recording and withdrawing it
are audited, and the prediction flow refuses to proceed without active
consent.
"""

from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import (
    ConsentServiceDep,
    PageParamsDep,
    PatientServiceDep,
)
from app.authentication.current_user import CurrentUserDep
from app.authorization.access_control import require_permission
from app.core.permissions import (
    CONSENTS_READ,
    CONSENTS_WRITE,
    PATIENTS_READ,
    PATIENTS_WRITE,
)
from app.models.consent import ConsentType
from app.schemas.pagination import Page
from app.schemas.patient import (
    ConsentCreate,
    ConsentRead,
    PatientCreate,
    PatientRead,
    PatientUpdate,
)

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.post(
    "",
    response_model=PatientRead,
    status_code=201,
    summary="Create a patient",
    dependencies=[Depends(require_permission(PATIENTS_WRITE))],
)
async def create_patient(
    payload: PatientCreate,
    service: PatientServiceDep,
    actor: CurrentUserDep,
) -> PatientRead:
    patient = await service.create_patient(
        patient_code=payload.patient_code,
        display_name=payload.display_name,
        date_of_birth=payload.date_of_birth,
        sex=payload.sex,
        actor=actor,
    )
    return PatientRead.model_validate(patient)


@router.get(
    "",
    response_model=Page[PatientRead],
    summary="Search patients",
    dependencies=[Depends(require_permission(PATIENTS_READ))],
)
async def list_patients(
    service: PatientServiceDep,
    params: PageParamsDep,
    query: Optional[str] = Query(default=None),
) -> Page[PatientRead]:
    items, total = await service.search(
        query=query, limit=params.limit, offset=params.offset
    )
    return Page.create(
        [PatientRead.model_validate(item) for item in items],
        total=total,
        page=params.page,
        page_size=params.page_size,
    )


@router.get(
    "/{patient_id}",
    response_model=PatientRead,
    summary="Get a patient",
    dependencies=[Depends(require_permission(PATIENTS_READ))],
)
async def get_patient(
    patient_id: uuid.UUID, service: PatientServiceDep
) -> PatientRead:
    patient = await service.get(patient_id)
    return PatientRead.model_validate(patient)


@router.patch(
    "/{patient_id}",
    response_model=PatientRead,
    summary="Update a patient",
    dependencies=[Depends(require_permission(PATIENTS_WRITE))],
)
async def update_patient(
    patient_id: uuid.UUID,
    payload: PatientUpdate,
    service: PatientServiceDep,
    actor: CurrentUserDep,
) -> PatientRead:
    patient = await service.get(patient_id)
    updated = await service.update_patient(
        patient,
        display_name=payload.display_name,
        date_of_birth=payload.date_of_birth,
        sex=payload.sex,
        actor=actor,
    )
    return PatientRead.model_validate(updated)


@router.post(
    "/{patient_id}/consents",
    response_model=ConsentRead,
    status_code=201,
    summary="Record consent",
    dependencies=[Depends(require_permission(CONSENTS_WRITE))],
)
async def grant_consent(
    patient_id: uuid.UUID,
    payload: ConsentCreate,
    service: ConsentServiceDep,
    actor: CurrentUserDep,
) -> ConsentRead:
    consent = await service.grant_consent(
        patient_id=patient_id,
        consent_type=ConsentType(payload.consent_type),
        expires_at=payload.expires_at,
        document_ref=payload.document_ref,
        actor=actor,
    )
    return ConsentRead.model_validate(consent)


@router.get(
    "/{patient_id}/consents",
    response_model=list[ConsentRead],
    summary="List consent records",
    dependencies=[Depends(require_permission(CONSENTS_READ))],
)
async def list_consents(
    patient_id: uuid.UUID, service: ConsentServiceDep
) -> list[ConsentRead]:
    consents = await service.list_for_patient(patient_id)
    return [ConsentRead.model_validate(consent) for consent in consents]


@router.post(
    "/{patient_id}/consents/{consent_id}/withdraw",
    response_model=ConsentRead,
    summary="Withdraw consent",
    dependencies=[Depends(require_permission(CONSENTS_WRITE))],
)
async def withdraw_consent(
    patient_id: uuid.UUID,
    consent_id: uuid.UUID,
    service: ConsentServiceDep,
    actor: CurrentUserDep,
) -> ConsentRead:
    consent = await service.get(consent_id)
    withdrawn = await service.withdraw_consent(consent, actor=actor)
    return ConsentRead.model_validate(withdrawn)
