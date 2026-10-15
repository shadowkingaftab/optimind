"""Authentication-related exceptions."""

from __future__ import annotations

from typing import Any, Mapping, Optional

from app.exceptions.base import APIException


class InvalidCredentialsError(APIException):
    status_code = 401
    error_code = "invalid_credentials"
    default_message = "The provided credentials are invalid."


class TokenExpiredError(APIException):
    status_code = 401
    error_code = "token_expired"
    default_message = "The authentication token has expired."


class TokenInvalidError(APIException):
    status_code = 401
    error_code = "token_invalid"
    default_message = "The authentication token is invalid."


class SessionNotFoundError(APIException):
    status_code = 401
    error_code = "session_not_found"
    default_message = "The session could not be found or has ended."


class AccountInactiveError(APIException):
    status_code = 403
    error_code = "account_inactive"
    default_message = "This account is not active."

    def __init__(
        self,
        message: Optional[str] = None,
        *,
        details: Optional[Mapping[str, Any]] = None,
    ) -> None:
        super().__init__(message, details=details)
