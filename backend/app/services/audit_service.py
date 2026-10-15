"""Audit service.

Thin service-layer wrapper over the audit logger and repository so that other
services depend on one collaborator for recording and querying audit trails.
"""

from __future__ import annotations

import uuid
from typing import Any, Optional, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.audit.audit_context import AuditContext
from app.audit.audit_events import STATUS_SUCCESS
from app.audit.audit_logger import AuditLogger
from app.models.audit_log import AuditLog
from app.repositories.audit_repository import AuditRepository


class AuditService:
    """Records and queries audit entries."""

    def __init__(self, session: AsyncSession) -> None:
        self._logger = AuditLogger(session)
        self._repository = AuditRepository(session)

    async def record(
        self,
        action: str,
        *,
        context: Optional[AuditContext] = None,
        actor_user_id: Optional[uuid.UUID] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        status: str = STATUS_SUCCESS,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        await self._logger.record(
            action,
            context=context,
            actor_user_id=actor_user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            status=status,
            metadata=metadata,
        )

    async def list_entries(
        self,
        *,
        actor_user_id: Optional[uuid.UUID] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[AuditLog]:
        return await self._repository.list_entries(
            actor_user_id=actor_user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            limit=limit,
            offset=offset,
        )
