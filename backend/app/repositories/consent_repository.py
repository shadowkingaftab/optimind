"""Consent persistence."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional, Sequence

from sqlalchemy import select

from app.models.consent import Consent, ConsentStatus, ConsentType
from app.repositories.base_repository import BaseRepository
from app.utils.datetime import utcnow


class ConsentRepository(BaseRepository[Consent]):
    model = Consent

    async def list_for_patient(self, patient_id: uuid.UUID) -> Sequence[Consent]:
        stmt = (
            select(Consent)
            .where(Consent.patient_id == patient_id)
            .order_by(Consent.created_at.desc())
        )
        return (await self.session.execute(stmt)).scalars().all()

    async def active_for_patient(
        self, patient_id: uuid.UUID, *, consent_type: ConsentType | None = None
    ) -> Optional[Consent]:
        now = utcnow()
        stmt = (
            select(Consent)
            .where(
                Consent.patient_id == patient_id,
                Consent.status == ConsentStatus.GRANTED,
                Consent.withdrawn_at.is_(None),
            )
            .where(
                (Consent.expires_at.is_(None)) | (Consent.expires_at > now)
            )
            .order_by(Consent.granted_at.desc().nullslast())
        )
        if consent_type is not None:
            stmt = stmt.where(Consent.consent_type == consent_type)
        return (await self.session.execute(stmt)).scalars().first()

    async def create(
        self,
        *,
        patient_id: uuid.UUID,
        consent_type: ConsentType = ConsentType.SCREENING,
        status: ConsentStatus = ConsentStatus.PENDING,
        expires_at: Optional[datetime] = None,
        document_ref: Optional[str] = None,
        recorded_by_user_id: Optional[uuid.UUID] = None,
    ) -> Consent:
        consent = Consent(
            patient_id=patient_id,
            consent_type=consent_type,
            status=status,
            granted_at=utcnow() if status is ConsentStatus.GRANTED else None,
            expires_at=expires_at,
            document_ref=document_ref,
            recorded_by_user_id=recorded_by_user_id,
        )
        return await self.add(consent)

    async def withdraw(self, consent: Consent) -> None:
        consent.status = ConsentStatus.WITHDRAWN
        consent.withdrawn_at = utcnow()
        await self.session.flush()
