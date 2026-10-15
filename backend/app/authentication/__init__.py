"""Authentication layer.

Public surface: password policy, token issuance, credential verification,
session lifecycle and the current-user dependencies.
"""

from __future__ import annotations

from app.authentication.authentication_backend import AuthenticationBackend
from app.authentication.current_user import (
    CurrentUserDep,
    OptionalUserDep,
    get_current_user,
    get_optional_current_user,
)
from app.authentication.password_hasher import (
    DEFAULT_PASSWORD_POLICY,
    PasswordPolicy,
    hash_password,
    needs_rehash,
    validate_password,
    verify_password,
)
from app.authentication.session_service import SessionService, SessionTokens
from app.authentication.token_service import TokenService

__all__ = [
    "DEFAULT_PASSWORD_POLICY",
    "AuthenticationBackend",
    "CurrentUserDep",
    "OptionalUserDep",
    "PasswordPolicy",
    "SessionService",
    "SessionTokens",
    "TokenService",
    "get_current_user",
    "get_optional_current_user",
    "hash_password",
    "needs_rehash",
    "validate_password",
    "verify_password",
]
