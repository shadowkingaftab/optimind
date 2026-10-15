"""Storage-related exceptions.

Storage identifiers (object keys, signed URLs, credentials) are treated as
sensitive and never included in outward-facing messages.
"""

from __future__ import annotations

from app.exceptions.base import APIException


class StorageError(APIException):
    status_code = 500
    error_code = "storage_error"
    default_message = "A storage error occurred while processing the request."


class StorageUnavailableError(APIException):
    status_code = 503
    error_code = "storage_unavailable"
    default_message = "The storage backend is temporarily unavailable."


class ObjectNotFoundError(APIException):
    status_code = 404
    error_code = "object_not_found"
    default_message = "The requested object could not be found."


class SignedUrlError(APIException):
    status_code = 403
    error_code = "signed_url_invalid"
    default_message = "The access link is invalid or has expired."


class StorageQuotaExceededError(APIException):
    status_code = 507
    error_code = "storage_quota_exceeded"
    default_message = "The storage quota has been exceeded."
