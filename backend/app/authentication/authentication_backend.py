"""Authentication backend: credential verification."""

from __future__ import annotations

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.authentication.password_hasher import verify_password
from app.exceptions.authentication import (
    AccountInactiveError,
    InvalidCredentialsError,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository


class AuthenticationBackend:
    """Verifies user credentials against persisted hashes."""

    def __init__(self, session: AsyncSession) -> None:
        self._users = UserRepository(session)

    async def get_by_email(self, email: str) -> Optional[User]:
        return await self._users.get_by_email(email)

    async def authenticate(self, *, email: str, password: str) -> User:
        """Return the user for valid credentials.

        Raises:
            InvalidCredentialsError: unknown email or wrong password.
            AccountInactiveError: credentials valid but account disabled.
        """
        user = await self._users.get_by_email(email)
        if user is None:
            # Run a dummy verification to reduce timing differences.
            verify_password(password, "$2b$12$" + "." * 53)
            raise InvalidCredentialsError()

        if not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError()

        if not user.is_active:
            raise AccountInactiveError()

        return user
