"""Security primitives: password hashing and JWT handling.

This module centralises all cryptographic concerns so that secrets and raw
credentials never leak into logs or API responses. It deliberately contains
no clinical or model logic.
"""

from __future__ import annotations

import hmac
import secrets
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import jwt
from passlib.context import CryptContext

from app.exceptions.authentication import TokenExpiredError, TokenInvalidError

# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------
_pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,
)


def hash_password(password: str) -> str:
    """Return a salted hash for ``password``."""
    return _pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a plaintext password against a stored hash (constant-time)."""
    try:
        return _pwd_context.verify(password, password_hash)
    except ValueError:
        # Malformed/unknown hash format -> treat as a failed verification.
        return False


def needs_rehash(password_hash: str) -> bool:
    """Return True when a stored hash should be upgraded."""
    try:
        return _pwd_context.needs_update(password_hash)
    except ValueError:
        return True


# ---------------------------------------------------------------------------
# Opaque token helpers (refresh tokens, email confirmations, etc.)
# ---------------------------------------------------------------------------
def generate_opaque_token(nbytes: int = 48) -> str:
    """Return a URL-safe opaque token."""
    return secrets.token_urlsafe(nbytes)


def hash_opaque_token(token: str) -> str:
    """Hash an opaque token for at-rest storage.

    Opaque tokens are high-entropy random strings, so a fast hash is
    appropriate; the plaintext is never persisted.
    """
    import hashlib

    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def constant_time_compare(a: str, b: str) -> bool:
    """Constant-time string comparison."""
    return hmac.compare_digest(a.encode("utf-8"), b.encode("utf-8"))


# ---------------------------------------------------------------------------
# JWT access tokens
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class TokenPayload:
    """Decoded, validated token claims."""

    subject: str
    expires_at: datetime
    issued_at: datetime
    token_type: str
    jti: str
    roles: tuple[str, ...] = ()


def create_access_token(
    subject: str,
    *,
    secret_key: str,
    algorithm: str = "HS256",
    expires_minutes: int = 60,
    roles: Optional[list[str]] = None,
    extra_claims: Optional[dict[str, Any]] = None,
) -> str:
    """Create a signed access token for ``subject`` (the user id)."""
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=expires_minutes)
    claims: dict[str, Any] = {
        "sub": str(subject),
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "jti": uuid.uuid4().hex,
        "type": "access",
        "roles": list(roles or []),
    }
    if extra_claims:
        # Caller-provided claims must not override reserved claims.
        for key, value in extra_claims.items():
            claims.setdefault(key, value)
    return jwt.encode(claims, secret_key, algorithm=algorithm)


def decode_token(
    token: str,
    *,
    secret_key: str,
    algorithm: str = "HS256",
    expected_type: Optional[str] = "access",
) -> TokenPayload:
    """Decode and validate a JWT.

    Raises:
        TokenExpiredError: when the token has expired.
        TokenInvalidError: for any other validation failure.
    """
    try:
        claims = jwt.decode(token, secret_key, algorithms=[algorithm])
    except jwt.ExpiredSignatureError as exc:
        raise TokenExpiredError() from exc
    except jwt.PyJWTError as exc:
        raise TokenInvalidError() from exc

    token_type = str(claims.get("type", "access"))
    if expected_type is not None and token_type != expected_type:
        raise TokenInvalidError("Unexpected token type.")

    subject = claims.get("sub")
    if not subject:
        raise TokenInvalidError("Token is missing a subject.")

    try:
        issued_at = datetime.fromtimestamp(int(claims["iat"]), tz=timezone.utc)
        expires_at = datetime.fromtimestamp(int(claims["exp"]), tz=timezone.utc)
    except (KeyError, TypeError, ValueError) as exc:
        raise TokenInvalidError("Token is missing required claims.") from exc

    roles_raw = claims.get("roles") or []
    roles = tuple(str(role) for role in roles_raw) if isinstance(roles_raw, list) else ()

    return TokenPayload(
        subject=str(subject),
        expires_at=expires_at,
        issued_at=issued_at,
        token_type=token_type,
        jti=str(claims.get("jti", "")),
        roles=roles,
    )
