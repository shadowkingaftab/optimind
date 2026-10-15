"""Consent service.

Consent is enforced explicitly: callers must obtain an active consent before
processing patient images. Absence of consent is never treated as granted.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.audit.audit_events import (
    ACTION_CONSENT_GRANT,
    ACTION_CONSENT_WITHDRAW,
    RESOURCE_CONSENT,
)
from app.audit.audit_logger import AuditLogger
from app.exceptions.authorization import ConsentExpiredError, ConsentRequiredError
from app.exceptions.base import NotFoundError
from app.models.consent import Consent, ConsentStatus, ConsentType
from app.models.user import User
from app.repositories.consent_repository import ConsentRepository


class ConsentService:
    """Manages patient consent records."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._consents = ConsentRepository(session)
        self._audit = AuditLogger(session)

    async def get(self, consent_id: uuid.UUID) -> Consent:
        consent = await self._consents.get(consent_id)
        if consent is None:
            raise NotFoundError("The requested consent was not found.")
        return consent

    async def list_for_patient(self, patient_id: uuid.UUID) -> Sequence[Consent]:
        return await self._consents.list_for_patient(patient_id)

    async def get_active(
        self,
        patient_id: uuid.UUID,
        *,
        consent_type: Optional[ConsentType] = None,
    ) -> Optional[Consent]:
        return await self._consents.active_for_patient(
            patient_id, consent_type=consent_type
        )

    async def require_active(
        self,
        patient_id: uuid.UUID,
        *,
        consent_type: Optional[ConsentType] = None,
    ) -> Consent:
        """Return an active consent or raise a consent error.

        Raises:
            ConsentExpiredError: a consent exists but has expired/withdrawn.
            ConsentRequiredError: no consent record exists at all.
        """
        active = await self._consents.active_for_patient(
            patient_id, consent_type=consent_type
        )
        if active is not None:
            return active

        existing = await self._consents.list_for_patient(patient_id)
        if existing:
            raise ConsentExpiredError()
        raise ConsentRequiredError()

    async def grant_consent(
        self,
        *,
        patient_id: uuid.UUID,
        consent_type: ConsentType = ConsentType.SCREENING,
        expires_at: Optional[datetime] = None,
        document_ref: Optional[str] = None,
        actor: Optional[User] = None,
    ) -> Consent:
        consent = await self._consents.create(
            patient_id=patient_id,
            consent_type=consent_type,
            status=ConsentStatus.GRANTED,
            expires_at=expires_at,
            document_ref=document_ref,
            recorded_by_user_id=actor.id if actor else None,
        )
        await self._audit.record(
            ACTION_CONSENT_GRANT,
            actor_user_id=actor.id if actor else None,
            resource_type=RESOURCE_CONSENT,
            resource_id=str(consent.id),
            metadata={"consent_type": str(consent_type)},
        )
        await self._session.commit()
        return consent

    async def withdraw_consent(
        self, consent: Consent, *, actor: Optional[User] = None
    ) -> Consent:
        await self._consents.withdraw(consent)
        await self._audit.record(
            ACTION_CONSENT_WITHDRAW,
            actor_user_id=actor.id if actor else None,
            resource_type=RESOURCE_CONSENT,
            resource_id=str(consent.id),
        )
        await self._session.commit()
        return consent
