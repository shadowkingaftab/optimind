"""Authentication service.

Coordinates credential verification, session issuance and audit recording.
Owns the transaction boundary: commits on success, relies on the request
rollback on failure, and writes failure audits independently so they persist.
"""

from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.audit.audit_events import (
    ACTION_LOGIN_FAILURE,
    ACTION_LOGIN_SUCCESS,
    ACTION_LOGOUT,
    ACTION_TOKEN_REFRESH,
    RESOURCE_SESSION,
    RESOURCE_USER,
    STATUS_FAILURE,
)
from app.audit.audit_logger import AuditLogger
from app.authentication.authentication_backend import AuthenticationBackend
from app.authentication.session_service import SessionService, SessionTokens
from app.exceptions.authentication import AccountInactiveError
from app.exceptions.base import APIException
from app.models.user import User
from app.repositories.user_repository import UserRepository


class AuthService:
    """Login, refresh and logout operations."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._backend = AuthenticationBackend(session)
        self._sessions = SessionService(session)
        self._users = UserRepository(session)
        self._audit = AuditLogger(session)

    async def login(
        self,
        *,
        email: str,
        password: str,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> tuple[User, SessionTokens]:
        try:
            user = await self._backend.authenticate(email=email, password=password)
        except APIException as exc:
            # Persist the attempt in an independent transaction so it survives
            # the request rollback triggered by re-raising.
            await self._audit.record_independent(
                ACTION_LOGIN_FAILURE,
                status=STATUS_FAILURE,
                ip_address=ip_address,
                user_agent=user_agent,
                metadata={"reason": getattr(exc, "error_code", "authentication_failed")},
            )
            raise

        tokens = await self._sessions.create_session(
            user, user_agent=user_agent, ip_address=ip_address
        )
        await self._users.record_login(user)
        await self._audit.record(
            ACTION_LOGIN_SUCCESS,
            actor_user_id=user.id,
            resource_type=RESOURCE_USER,
            resource_id=str(user.id),
        )
        await self._session.commit()
        return user, tokens

    async def refresh(
        self,
        *,
        refresh_token: str,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> tuple[User, SessionTokens]:
        stored = await self._sessions.resolve_refresh_token(refresh_token)
        user = await self._users.get(stored.user_id)
        if user is None:
            from app.exceptions.authentication import SessionNotFoundError

            raise SessionNotFoundError()
        if not user.is_active:
            raise AccountInactiveError()

        tokens = await self._sessions.rotate(
            refresh_token, user=user, user_agent=user_agent, ip_address=ip_address
        )
        await self._audit.record(
            ACTION_TOKEN_REFRESH,
            actor_user_id=user.id,
            resource_type=RESOURCE_SESSION,
            resource_id=str(user.id),
        )
        await self._session.commit()
        return user, tokens

    async def logout(
        self, *, refresh_token: str, user: Optional[User] = None
    ) -> None:
        await self._sessions.revoke(refresh_token)
        await self._audit.record(
            ACTION_LOGOUT,
            actor_user_id=user.id if user is not None else None,
            resource_type=RESOURCE_SESSION,
        )
        await self._session.commit()

    async def revoke_all_sessions(self, user_id: uuid.UUID) -> int:
        revoked = await self._sessions.revoke_all_for_user(user_id)
        await self._session.commit()
        return revoked
