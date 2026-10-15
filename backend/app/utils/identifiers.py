"""Identifier generation helpers.

Identifiers remain opaque to end users and never encode clinical data.
"""

from __future__ import annotations

import secrets
import uuid


def new_uuid() -> uuid.UUID:
    """Generate a new UUID4."""
    return uuid.uuid4()


def new_uuid_str() -> str:
    """Generate a new UUID4 as a canonical string."""
    return str(uuid.uuid4())


def generate_reference(prefix: str = "ref") -> str:
    """Generate a short pseudonymous reference token."""
    return f"{prefix}-{secrets.token_hex(8)}"


def generate_token(nbytes: int = 32) -> str:
    """Generate a URL-safe random token."""
    return secrets.token_urlsafe(nbytes)
