"""Audit request context.

Captures the actor and request identifiers attached to an audited action.
Values are populated from the request-scoped context so callers do not thread
them through manually.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Optional

from app.core.request_context import get_correlation_id, get_request_id


@dataclass(frozen=True)
class AuditContext:
    """Immutable context describing who did what, from where."""

    actor_user_id: Optional[uuid.UUID] = None
    request_id: Optional[str] = None
    correlation_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    @classmethod
    def current(
        cls,
        *,
        actor_user_id: Optional[uuid.UUID] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> "AuditContext":
        """Build a context, pulling request ids from the ambient context."""
        return cls(
            actor_user_id=actor_user_id,
            request_id=get_request_id(),
            correlation_id=get_correlation_id(),
            ip_address=ip_address,
            user_agent=user_agent,
        )
