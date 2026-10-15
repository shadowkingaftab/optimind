"""Token issuance and validation.

Wraps :mod:`app.core.security` with application settings. Access tokens are
signed JWTs; refresh tokens are opaque random strings stored only as hashes.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from app.core.security import (
    TokenPayload,
    create_access_token,
    decode_token,
    generate_opaque_token,
    hash_opaque_token,
)
from app.core.settings import Settings, get_settings
from app.utils.datetime import ensure_utc, utcnow


class TokenService:
    """Issues and validates authentication tokens."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self._settings = settings or get_settings()

    @property
    def _secret(self) -> str:
        secret = self._settings.jwt_secret_key
        if secret is None or not secret.get_secret_value():
            # validate_for_startup() generates an ephemeral dev secret; this
            # guard only triggers if TokenService is used before startup.
            from app.exceptions.base import ConfigurationError

            raise ConfigurationError("JWT secret is not configured.")
        return secret.get_secret_value()

    def create_access_token(
        self, subject: str, *, roles: Optional[list[str]] = None
    ) -> str:
        return create_access_token(
            subject,
            secret_key=self._secret,
            algorithm=self._settings.jwt_algorithm,
            expires_minutes=self._settings.jwt_expiry_minutes,
            roles=roles,
        )

    def decode_access_token(self, token: str) -> TokenPayload:
        return decode_token(
            token,
            secret_key=self._secret,
            algorithm=self._settings.jwt_algorithm,
            expected_type="access",
        )

    def create_refresh_token(self) -> tuple[str, str, datetime]:
        """Return ``(plaintext, hash, expires_at)`` for a new refresh token."""
        plaintext = generate_opaque_token()
        token_hash = hash_opaque_token(plaintext)
        expires_at = utcnow() + timedelta(
            days=self._settings.refresh_token_expiry_days
        )
        return plaintext, token_hash, expires_at

    def hash_refresh_token(self, plaintext: str) -> str:
        return hash_opaque_token(plaintext)

    def is_expired(self, expires_at: datetime) -> bool:
        return ensure_utc(expires_at) <= utcnow()
