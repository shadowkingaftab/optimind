"""Patient persistence."""

from __future__ import annotations

import uuid
from datetime import date
from typing import Optional, Sequence

from sqlalchemy import func, select

from app.models.patient import Patient
from app.repositories.base_repository import BaseRepository


class PatientRepository(BaseRepository[Patient]):
    model = Patient

    async def get_by_code(self, patient_code: str) -> Optional[Patient]:
        stmt = select(Patient).where(Patient.patient_code == patient_code)
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def code_exists(self, patient_code: str) -> bool:
        return await self.get_by_code(patient_code) is not None

    async def search(
        self,
        *,
        query: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[Patient]:
        stmt = select(Patient).order_by(Patient.created_at.desc())
        if query:
            pattern = f"%{query.strip()}%"
            stmt = stmt.where(
                Patient.patient_code.ilike(pattern)
                | Patient.display_name.ilike(pattern)
            )
        stmt = stmt.offset(offset).limit(limit)
        return (await self.session.execute(stmt)).scalars().all()

    async def count_search(self, query: Optional[str] = None) -> int:
        stmt = select(func.count()).select_from(Patient)
        if query:
            pattern = f"%{query.strip()}%"
            stmt = stmt.where(
                Patient.patient_code.ilike(pattern)
                | Patient.display_name.ilike(pattern)
            )
        return int((await self.session.execute(stmt)).scalar() or 0)

    async def create(
        self,
        *,
        patient_code: str,
        display_name: Optional[str] = None,
        date_of_birth: Optional[date] = None,
        sex: Optional[str] = None,
        created_by_user_id: Optional[uuid.UUID] = None,
    ) -> Patient:
        patient = Patient(
            patient_code=patient_code,
            display_name=display_name,
            date_of_birth=date_of_birth,
            sex=sex,
            created_by_user_id=created_by_user_id,
        )
        return await self.add(patient)
