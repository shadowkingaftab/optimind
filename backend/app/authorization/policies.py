"""Authorization policy helpers.

Pure functions evaluating whether a user may perform an action. Kept free of
FastAPI so they can be reused by services and background jobs.
"""

from __future__ import annotations

import uuid
from typing import Optional

from app.authorization.roles import is_admin, permissions_of
from app.exceptions.authorization import PermissionDeniedError
from app.models.user import User


def has_permission(user: User, permission: str) -> bool:
    """Return True when the user is granted ``permission``."""
    if is_admin(user):
        return True
    return permission in permissions_of(user)


def require_permission(user: User, permission: str) -> None:
    """Raise ``PermissionDeniedError`` unless the user has ``permission``."""
    if not has_permission(user, permission):
        raise PermissionDeniedError()


def is_owner(user: User, owner_user_id: Optional[uuid.UUID]) -> bool:
    """Return True when the user owns the resource."""
    return owner_user_id is not None and owner_user_id == user.id


def can_access_patient_record(
    user: User,
    *,
    owner_user_id: Optional[uuid.UUID],
    read_permission: str,
) -> bool:
    """Return True when the user may read a patient-scoped record.

    Access is granted to admins, the record creator, or any user holding the
    relevant read permission.
    """
    if is_admin(user) or is_owner(user, owner_user_id):
        return True
    return has_permission(user, read_permission)


__all__ = [
    "can_access_patient_record",
    "has_permission",
    "is_owner",
    "require_permission",
]
