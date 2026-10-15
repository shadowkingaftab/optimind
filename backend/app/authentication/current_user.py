"""Current-user resolution dependencies.

Resolves the bearer token to an authenticated :class:`User`, attaches the
subject to the request context, and enforces the active-account check.
"""

from __future__ import annotations

import uuid
from typing import Annotated, Optional

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.authentication.token_service import TokenService
from app.core.request_context import with_user
from app.database.session import get_db
from app.exceptions.authentication import (
    AccountInactiveError,
    TokenInvalidError,
)
from app.exceptions.base import AuthenticationError
from app.models.user import User
from app.repositories.user_repository import UserRepository

_bearer_scheme = HTTPBearer(auto_error=False, scheme_name="Bearer")

CredentialsDep = Annotated[
    Optional[HTTPAuthorizationCredentials], Depends(_bearer_scheme)
]
SessionDep = Annotated[AsyncSession, Depends(get_db)]


async def get_optional_current_user(
    credentials: CredentialsDep,
    session: SessionDep,
) -> Optional[User]:
    """Return the authenticated user, or ``None`` when no token is supplied."""
    if credentials is None or not credentials.credentials:
        return None
    return await _resolve_user(credentials.credentials, session)


async def get_current_user(
    credentials: CredentialsDep,
    session: SessionDep,
) -> User:
    """Return the authenticated user or raise a 401."""
    if credentials is None or not credentials.credentials:
        raise AuthenticationError()
    return await _resolve_user(credentials.credentials, session)


async def _resolve_user(token: str, session: AsyncSession) -> User:
    payload = TokenService().decode_access_token(token)
    try:
        user_id = uuid.UUID(payload.subject)
    except (ValueError, TypeError) as exc:
        raise TokenInvalidError("Token subject is not a valid user id.") from exc

    user = await UserRepository(session).get(user_id)
    if user is None:
        raise AuthenticationError()
    if not user.is_active:
        raise AccountInactiveError()

    with_user(str(user.id))
    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]
OptionalUserDep = Annotated[Optional[User], Depends(get_optional_current_user)]
