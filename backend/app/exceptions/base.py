"""Base exception types for the EyeDx backend.

All domain exceptions derive from :class:`APIException`. The FastAPI exception
handlers in ``app.core.exception_handlers`` translate these into the shared
ErrorResponse contract (``contracts/json-schemas/error-response.schema.json``).

Design rules:
    * Error codes are stable, machine-readable strings (snake_case).
    * Messages are screening-safe and never contain credentials, tokens, image
      data or other sensitive values.
    * Stack traces are never exposed to API consumers.
"""

from __future__ import annotations

from typing import Any, Mapping, Optional


class APIException(Exception):
    """Base class for all handled application errors.

    Attributes:
        status_code: HTTP status to return.
        error_code: Stable machine-readable code (matches the ``error`` field
            of the shared ErrorResponse contract).
        message: Human-readable, non-sensitive message.
        details: Optional structured, non-sensitive details.
    """

    status_code: int = 500
    error_code: str = "internal_error"
    default_message: str = "An unexpected error occurred."

    def __init__(
        self,
        message: Optional[str] = None,
        *,
        details: Optional[Mapping[str, Any]] = None,
        status_code: Optional[int] = None,
        error_code: Optional[str] = None,
    ) -> None:
        self.message: str = message or self.default_message
        self.details: Optional[dict[str, Any]] = (
            dict(details) if details is not None else None
        )
        if status_code is not None:
            self.status_code = status_code
        if error_code is not None:
            self.error_code = error_code
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        """Return a contract-shaped error body (without request_id).

        The request_id is injected by the exception handler from request
        context so that every error remains traceable.
        """
        body: dict[str, Any] = {
            "error": self.error_code,
            "message": self.message,
        }
        if self.details:
            body["details"] = self.details
        return body


class BadRequestError(APIException):
    status_code = 400
    error_code = "bad_request"
    default_message = "The request could not be processed."


class APIValidationError(APIException):
    status_code = 422
    error_code = "validation_failed"
    default_message = "The request failed validation."


class AuthenticationError(APIException):
    status_code = 401
    error_code = "unauthorized"
    default_message = "Authentication is required."


class AuthorizationError(APIException):
    status_code = 403
    error_code = "forbidden"
    default_message = "You are not permitted to perform this action."


class NotFoundError(APIException):
    status_code = 404
    error_code = "not_found"
    default_message = "The requested resource was not found."


class ConflictError(APIException):
    status_code = 409
    error_code = "conflict"
    default_message = "The request conflicts with the current state."


class PayloadTooLargeError(APIException):
    status_code = 413
    error_code = "payload_too_large"
    default_message = "The uploaded payload exceeds the allowed size."


class UnsupportedMediaTypeError(APIException):
    status_code = 415
    error_code = "unsupported_media_type"
    default_message = "The uploaded media type is not supported."


class RateLimitError(APIException):
    status_code = 429
    error_code = "rate_limited"
    default_message = "Too many requests. Please retry later."


class ConfigurationError(APIException):
    status_code = 500
    error_code = "configuration_error"
    default_message = "The service is not configured correctly."


class ServiceUnavailableError(APIException):
    status_code = 503
    error_code = "service_unavailable"
    default_message = "The service is temporarily unavailable."
