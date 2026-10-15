"""HMAC-signed access tokens for local storage.

Local storage has no native presign capability, so access is granted via a
short-lived, HMAC-signed token that the (future) file-serving route verifies.
Keys are validated to prevent path traversal.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from typing import Optional


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def sign_token(
    key: str,
    *,
    secret: str,
    expires_seconds: int = 300,
    now: Optional[float] = None,
) -> str:
    """Create an HMAC-signed token for ``key``."""
    issued = int(now if now is not None else time.time())
    payload = {"k": key, "exp": issued + max(1, int(expires_seconds))}
    body = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signature = hmac.new(secret.encode("utf-8"), body.encode("ascii"), hashlib.sha256)
    return f"{body}.{_b64url_encode(signature.digest())}"


def verify_token(token: str, *, secret: str, now: Optional[float] = None) -> str:
    """Verify a signed token and return its key.

    Raises:
        SignedUrlError: when the token is malformed, forged or expired.
    """
    from app.exceptions.storage import SignedUrlError

    try:
        body, signature = token.split(".", 1)
    except ValueError as exc:
        raise SignedUrlError() from exc

    expected = hmac.new(
        secret.encode("utf-8"), body.encode("ascii"), hashlib.sha256
    ).digest()
    try:
        provided = _b64url_decode(signature)
    except Exception as exc:  # noqa: BLE001
        raise SignedUrlError() from exc

    if not hmac.compare_digest(expected, provided):
        raise SignedUrlError()

    try:
        payload = json.loads(_b64url_decode(body))
        key = str(payload["k"])
        exp = int(payload["exp"])
    except (KeyError, ValueError, TypeError) as exc:
        raise SignedUrlError() from exc

    current = int(now if now is not None else time.time())
    if current >= exp:
        raise SignedUrlError("The access link has expired.")
    return key
