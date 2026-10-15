"""Permission catalogue and role-to-permission mapping.

This module is the single source of truth for coarse-grained RBAC. Policy
enforcement (dependency guards, ownership checks) lives in
``app.authorization`` and is wired up in Phase 3; here we only define the
vocabulary so routes, services and tests share one definition.
"""

from __future__ import annotations

from typing import Final, Iterable

from app.core.constants import (
    ROLE_ADMIN,
    ROLE_CLINICIAN,
    ROLE_OPERATOR,
    ROLE_RESEARCHER,
)

# ---------------------------------------------------------------------------
# Permission identifiers (``resource:action``)
# ---------------------------------------------------------------------------
USERS_READ: Final[str] = "users:read"
USERS_WRITE: Final[str] = "users:write"

PATIENTS_READ: Final[str] = "patients:read"
PATIENTS_WRITE: Final[str] = "patients:write"

CONSENTS_READ: Final[str] = "consents:read"
CONSENTS_WRITE: Final[str] = "consents:write"

UPLOADS_CREATE: Final[str] = "uploads:create"
UPLOADS_READ: Final[str] = "uploads:read"

PREDICTIONS_CREATE: Final[str] = "predictions:create"
PREDICTIONS_READ: Final[str] = "predictions:read"

REPORTS_READ: Final[str] = "reports:read"
REPORTS_GENERATE: Final[str] = "reports:generate"

MODELS_READ: Final[str] = "models:read"
MODELS_MANAGE: Final[str] = "models:manage"

AUDIT_READ: Final[str] = "audit:read"
ADMIN_MANAGE: Final[str] = "admin:manage"

ALL_PERMISSIONS: Final[frozenset[str]] = frozenset(
    {
        USERS_READ,
        USERS_WRITE,
        PATIENTS_READ,
        PATIENTS_WRITE,
        CONSENTS_READ,
        CONSENTS_WRITE,
        UPLOADS_CREATE,
        UPLOADS_READ,
        PREDICTIONS_CREATE,
        PREDICTIONS_READ,
        REPORTS_READ,
        REPORTS_GENERATE,
        MODELS_READ,
        MODELS_MANAGE,
        AUDIT_READ,
        ADMIN_MANAGE,
    }
)

# ---------------------------------------------------------------------------
# Role definitions
# ---------------------------------------------------------------------------
ROLE_PERMISSIONS: Final[dict[str, frozenset[str]]] = {
    ROLE_ADMIN: ALL_PERMISSIONS,
    ROLE_CLINICIAN: frozenset(
        {
            PATIENTS_READ,
            PATIENTS_WRITE,
            CONSENTS_READ,
            CONSENTS_WRITE,
            UPLOADS_CREATE,
            UPLOADS_READ,
            PREDICTIONS_CREATE,
            PREDICTIONS_READ,
            REPORTS_READ,
            REPORTS_GENERATE,
            MODELS_READ,
        }
    ),
    ROLE_OPERATOR: frozenset(
        {
            PATIENTS_READ,
            UPLOADS_CREATE,
            UPLOADS_READ,
            PREDICTIONS_CREATE,
            PREDICTIONS_READ,
            REPORTS_READ,
            MODELS_READ,
        }
    ),
    ROLE_RESEARCHER: frozenset(
        {
            PATIENTS_READ,
            PREDICTIONS_READ,
            REPORTS_READ,
            MODELS_READ,
            AUDIT_READ,
        }
    ),
}


def permissions_for_roles(roles: Iterable[str]) -> frozenset[str]:
    """Return the union of permissions granted by ``roles``."""
    granted: set[str] = set()
    for role in roles:
        granted.update(ROLE_PERMISSIONS.get(role, frozenset()))
    return frozenset(granted)


def has_permission(roles: Iterable[str], permission: str) -> bool:
    """Return True when any role in ``roles`` grants ``permission``."""
    return permission in permissions_for_roles(roles)


def has_any_permission(roles: Iterable[str], permissions: Iterable[str]) -> bool:
    """Return True when ``roles`` grants at least one of ``permissions``."""
    granted = permissions_for_roles(roles)
    return any(permission in granted for permission in permissions)
