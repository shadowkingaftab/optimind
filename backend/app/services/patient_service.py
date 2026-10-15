"""Patient service.

Patient records are pseudonymous by default: callers supply a patient code
(or one is generated) and optional, non-required identity fields. No clinical
values are produced here.
"""

from __future__ import annotations

import uuid
from datetime import date
from typing import Optional, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.audit.audit_events import (
    ACTION_PATIENT_CREATE,
    ACTION_PATIENT_UPDATE,
    RESOURCE_PATIENT,
)
from app.audit.audit_logger import AuditLogger
from app.exceptions.base import ConflictError, NotFoundError
from app.models.patient import Patient
from app.models.user import User
from app.repositories.patient_repository import PatientRepository
from app.utils.identifiers import generate_reference


class PatientService:
    """Creation and retrieval of patient records."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._patients = PatientRepository(session)
        self._audit = AuditLogger(session)

    async def get(self, patient_id: uuid.UUID) -> Patient:
        patient = await self._patients.get(patient_id)
        if patient is None:
            raise NotFoundError("The requested patient was not found.")
        return patient

    async def get_by_code(self, patient_code: str) -> Optional[Patient]:
        return await self._patients.get_by_code(patient_code)

    async def search(
        self,
        *,
        query: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[Sequence[Patient], int]:
        items = await self._patients.search(
            query=query, limit=limit, offset=offset
        )
        total = await self._patients.count_search(query)
        return items, total

    async def create_patient(
        self,
        *,
        patient_code: Optional[str] = None,
        display_name: Optional[str] = None,
        date_of_birth: Optional[date] = None,
        sex: Optional[str] = None,
        actor: Optional[User] = None,
    ) -> Patient:
        code = (patient_code or "").strip() or generate_reference("pt")
        if await self._patients.get_by_code(code) is not None:
            raise ConflictError("A patient with this code already exists.")

        patient = await self._patients.create(
            patient_code=code,
            display_name=display_name,
            date_of_birth=date_of_birth,
            sex=sex,
            created_by_user_id=actor.id if actor else None,
        )
        await self._audit.record(
            ACTION_PATIENT_CREATE,
            actor_user_id=actor.id if actor else None,
            resource_type=RESOURCE_PATIENT,
            resource_id=str(patient.id),
        )
        await self._session.commit()
        return patient

    async def update_patient(
        self,
        patient: Patient,
        *,
        display_name: Optional[str] = None,
        date_of_birth: Optional[date] = None,
        sex: Optional[str] = None,
        actor: Optional[User] = None,
    ) -> Patient:
        if display_name is not None:
            patient.display_name = display_name
        if date_of_birth is not None:
            patient.date_of_birth = date_of_birth
        if sex is not None:
            patient.sex = sex
        await self._session.flush()
        await self._audit.record(
            ACTION_PATIENT_UPDATE,
            actor_user_id=actor.id if actor else None,
            resource_type=RESOURCE_PATIENT,
            resource_id=str(patient.id),
        )
        await self._session.commit()
        return patient
