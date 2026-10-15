"""Audit logger.

Writes immutable audit entries through :class:`AuditRepository`. Records
structural facts only: no image data, credentials or free-text clinical
values are stored. The logger flushes within the caller's transaction so an
audit record and the action it describes commit atomically.
"""

from __future__ import annotations

import uuid
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.audit.audit_context import AuditContext
from app.audit.audit_events import STATUS_FAILURE, STATUS_SUCCESS
from app.repositories.audit_repository import AuditRepository


class AuditLogger:
    """Records audit entries for a session."""

    def __init__(self, session: AsyncSession) -> None:
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
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> None:
        """Persist a single audit entry."""
        ctx = context or AuditContext.current(
            actor_user_id=actor_user_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        await self._repository.record(
            action=action,
            actor_user_id=ctx.actor_user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            status=status,
            request_id=ctx.request_id,
            correlation_id=ctx.correlation_id,
            ip_address=ctx.ip_address,
            user_agent=ctx.user_agent,
            metadata=metadata,
        )

    async def success(
        self,
        action: str,
        *,
        context: Optional[AuditContext] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        await self.record(
            action,
            context=context,
            resource_type=resource_type,
            resource_id=resource_id,
            status=STATUS_SUCCESS,
            metadata=metadata,
        )

    async def failure(
        self,
        action: str,
        *,
        context: Optional[AuditContext] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        await self.record(
            action,
            context=context,
            resource_type=resource_type,
            resource_id=resource_id,
            status=STATUS_FAILURE,
            metadata=metadata,
        )

    async def record_independent(
        self,
        action: str,
        *,
        context: Optional[AuditContext] = None,
        actor_user_id: Optional[uuid.UUID] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        status: str = STATUS_SUCCESS,
        metadata: Optional[dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> None:
        """Record in a separate committed transaction.

        Use for events that must survive a request rollback (for example a
        failed login): the caller's transaction may be rolled back when the
        request ends, but an attempted-access record must remain.
        """
        from app.database.session import session_scope

        ctx = context or AuditContext.current(
            actor_user_id=actor_user_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        async with session_scope() as session:
            await AuditLogger(session).record(
                action,
                context=ctx,
                resource_type=resource_type,
                resource_id=resource_id,
                status=status,
                metadata=metadata,
            )
