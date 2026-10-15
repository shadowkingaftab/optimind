"""System event persistence (operational, non-clinical)."""

from __future__ import annotations

from typing import Any, Optional, Sequence

from sqlalchemy import select

from app.models.system_event import EventSeverity, SystemEvent
from app.repositories.base_repository import BaseRepository


class SystemEventRepository(BaseRepository[SystemEvent]):
    model = SystemEvent

    async def record(
        self,
        *,
        event_type: str,
        message: str,
        severity: EventSeverity = EventSeverity.INFO,
        request_id: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> SystemEvent:
        event = SystemEvent(
            event_type=event_type,
            message=message,
            severity=severity,
            request_id=request_id,
            extra_metadata=metadata,
        )
        return await self.add(event)

    async def list_recent(
        self,
        *,
        event_type: Optional[str] = None,
        severity: Optional[EventSeverity] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[SystemEvent]:
        stmt = select(SystemEvent).order_by(SystemEvent.created_at.desc())
        if event_type is not None:
            stmt = stmt.where(SystemEvent.event_type == event_type)
        if severity is not None:
            stmt = stmt.where(SystemEvent.severity == severity)
        stmt = stmt.offset(offset).limit(limit)
        return (await self.session.execute(stmt)).scalars().all()
