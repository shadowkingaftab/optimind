"""FastAPI access-control dependencies.

Builds reusable guards from the permission catalogue. Route modules depend on
these instead of re-implementing role checks.
"""

from __future__ import annotations

from typing import Callable

from fastapi import Depends

from app.authentication.current_user import get_current_user
from app.authorization.roles import is_admin
from app.exceptions.authorization import PermissionDeniedError
from app.models.user import User


def require_permission(permission: str) -> Callable[[User], User]:
    """Return a dependency that requires ``permission``."""

    async def _guard(user: User = Depends(get_current_user)) -> User:
        from app.authorization.policies import has_permission

        if not has_permission(user, permission):
            raise PermissionDeniedError()
        return user

    return _guard


def require_admin() -> Callable[[User], User]:
    """Return a dependency that requires the admin role."""

    async def _guard(user: User = Depends(get_current_user)) -> User:
        if not is_admin(user):
            raise PermissionDeniedError()
        return user

    return _guard


__all__ = ["require_admin", "require_permission"]
