"""Role helpers.

Role names are defined in :mod:`app.core.constants`; the role-to-permission
mapping lives in :mod:`app.core.permissions`. These helpers read a user's
effective role without duplicating that vocabulary.
"""

from __future__ import annotations

from typing import Optional

from app.core.constants import (
    DEFAULT_ROLES,
    ROLE_ADMIN,
    ROLE_CLINICIAN,
    ROLE_OPERATOR,
    ROLE_RESEARCHER,
)
from app.core.permissions import permissions_for_roles
from app.models.user import User


def role_name(user: User) -> Optional[str]:
    """Return the user's role name, if assigned."""
    if user.role is None:
        return None
    return user.role.name


def roles_of(user: User) -> tuple[str, ...]:
    """Return the effective role list for a user."""
    name = role_name(user)
    return (name,) if name else ()


def permissions_of(user: User) -> frozenset[str]:
    """Return the permissions granted to a user."""
    return permissions_for_roles(roles_of(user))


def is_admin(user: User) -> bool:
    """Return True when the user holds the admin role or is a superuser."""
    return user.is_superuser or role_name(user) == ROLE_ADMIN


def is_known_role(name: str) -> bool:
    """Return True when ``name`` is a defined system role."""
    return name in DEFAULT_ROLES


__all__ = [
    "ROLE_ADMIN",
    "ROLE_CLINICIAN",
    "ROLE_OPERATOR",
    "ROLE_RESEARCHER",
    "is_admin",
    "is_known_role",
    "permissions_of",
    "role_name",
    "roles_of",
]
