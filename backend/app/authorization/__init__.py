"""Authorization layer.

Role helpers, pure policy functions and FastAPI access-control guards. The
permission catalogue itself is owned by :mod:`app.core.permissions`.
"""

from __future__ import annotations

from app.authorization.access_control import require_admin, require_permission
from app.authorization.policies import (
    can_access_patient_record,
    has_permission,
    is_owner,
    require_permission as check_permission,
)
from app.authorization.roles import (
    ROLE_ADMIN,
    ROLE_CLINICIAN,
    ROLE_OPERATOR,
    ROLE_RESEARCHER,
    is_admin,
    is_known_role,
    permissions_of,
    role_name,
    roles_of,
)

__all__ = [
    "ROLE_ADMIN",
    "ROLE_CLINICIAN",
    "ROLE_OPERATOR",
    "ROLE_RESEARCHER",
    "can_access_patient_record",
    "check_permission",
    "has_permission",
    "is_admin",
    "is_known_role",
    "is_owner",
    "permissions_of",
    "require_admin",
    "require_permission",
    "role_name",
    "roles_of",
]
