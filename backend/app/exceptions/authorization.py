"""Authorization-related exceptions."""

from __future__ import annotations

from app.exceptions.base import APIException


class PermissionDeniedError(APIException):
    status_code = 403
    error_code = "permission_denied"
    default_message = "You do not have permission to perform this action."


class ConsentRequiredError(APIException):
    """Raised when an action requires a valid, active consent record."""

    status_code = 403
    error_code = "consent_required"
    default_message = "A valid consent record is required for this action."


class ConsentExpiredError(APIException):
    status_code = 403
    error_code = "consent_expired"
    default_message = "The associated consent has expired or been withdrawn."


class RoleAssignmentError(APIException):
    status_code = 403
    error_code = "role_assignment_forbidden"
    default_message = "This role change is not permitted."
