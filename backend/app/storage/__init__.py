"""Storage package and backend factory.

Selects the storage backend from settings. The local backend signs access
tokens with the application secret; object storage uses native presigning.
"""

from __future__ import annotations

import secrets
from typing import Optional

from app.core.logging_config import get_logger
from app.core.settings import get_settings
from app.storage.storage_interface import StorageBackend, StoredObject

logger = get_logger(__name__)

_backend: Optional[StorageBackend] = None
_fallback_secret = secrets.token_urlsafe(32)


def _signing_secret() -> str:
    secret = get_settings().jwt_secret_key
    if secret is not None and secret.get_secret_value():
        return secret.get_secret_value()
    return _fallback_secret


def get_storage() -> StorageBackend:
    """Return the configured storage backend (cached)."""
    global _backend
    if _backend is not None:
        return _backend

    settings = get_settings()
    backend = settings.storage_backend.strip().lower()
    if backend in ("s3", "object", "object_storage"):
        from app.storage.object_storage import ObjectStorage

        _backend = ObjectStorage(
            bucket=settings.s3_bucket or "",
            region=settings.s3_region,
            endpoint_url=settings.s3_endpoint_url,
            access_key_id=(
                settings.s3_access_key_id.get_secret_value()
                if settings.s3_access_key_id
                else None
            ),
            secret_access_key=(
                settings.s3_secret_access_key.get_secret_value()
                if settings.s3_secret_access_key
                else None
            ),
        )
    else:
        from app.storage.local_storage import LocalStorage

        _backend = LocalStorage(
            settings.storage_local_path, signing_secret=_signing_secret()
        )
    return _backend


def reset_storage() -> None:
    """Clear the cached backend (used on shutdown / in tests)."""
    global _backend
    _backend = None


__all__ = [
    "StorageBackend",
    "StoredObject",
    "get_storage",
    "reset_storage",
]
