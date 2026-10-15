"""Session and refresh-token lifecycle."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.authentication.token_service import TokenService
from app.exceptions.authentication import SessionNotFoundError, TokenInvalidError
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.repositories.refresh_token_repository import RefreshTokenRepository


@dataclass(frozen=True)
class SessionTokens:
    access_token: str
    refresh_token: str
    refresh_expires_at: datetime


class SessionService:
    """Creates, rotates and revokes authenticated sessions."""

    def __init__(
        self, session: AsyncSession, *, token_service: Optional[TokenService] = None
    ) -> None:
        self._session = session
        self._tokens = token_service or TokenService()
        self._refresh = RefreshTokenRepository(session)

    async def create_session(
        self,
        user: User,
        *,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> SessionTokens:
        roles = [user.role.name] if user.role is not None else []
        access = self._tokens.create_access_token(str(user.id), roles=roles)
        plaintext, token_hash, expires_at = self._tokens.create_refresh_token()
        await self._refresh.create(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        return SessionTokens(
            access_token=access,
            refresh_token=plaintext,
            refresh_expires_at=expires_at,
        )

    async def _get_active(self, refresh_plain: str) -> RefreshToken:
        token_hash = self._tokens.hash_refresh_token(refresh_plain)
        stored = await self._refresh.get_by_hash(token_hash)
        if stored is None:
            raise SessionNotFoundError()
        if stored.is_revoked:
            raise TokenInvalidError("The session has been revoked.")
        if self._tokens.is_expired(stored.expires_at):
            raise TokenInvalidError("The session has expired.")
        return stored

    async def resolve_refresh_token(self, refresh_plain: str) -> RefreshToken:
        """Return the active refresh-token record or raise."""
        return await self._get_active(refresh_plain)

    async def rotate(
        self,
        refresh_plain: str,
        *,
        user: User,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> SessionTokens:
        """Revoke the presented refresh token and issue a new session."""
        stored = await self._get_active(refresh_plain)
        await self._refresh.revoke(stored)
        return await self.create_session(
            user, user_agent=user_agent, ip_address=ip_address
        )

    async def revoke(self, refresh_plain: str) -> None:
        token_hash = self._tokens.hash_refresh_token(refresh_plain)
        stored = await self._refresh.get_by_hash(token_hash)
        if stored is None or stored.is_revoked:
            return
        await self._refresh.revoke(stored)

    async def revoke_all_for_user(self, user_id: uuid.UUID) -> int:
        return await self._refresh.revoke_all_for_user(user_id)

    async def list_sessions(self, user_id: uuid.UUID) -> Sequence[RefreshToken]:
        return await self._refresh.list_for_user(user_id)
