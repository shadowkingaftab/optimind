"""Storage backend interface.

Backends store opaque bytes under caller-provided keys and never inspect or
log content. All operations are async-friendly but may run blocking IO.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class StoredObject:
    key: str
    size_bytes: int
    checksum_sha256: Optional[str] = None


class StorageBackend(ABC):
    """Abstract storage backend."""

    @abstractmethod
    async def put(
        self,
        key: str,
        data: bytes,
        *,
        content_type: str = "application/octet-stream",
    ) -> StoredObject:
        """Store ``data`` under ``key`` (overwriting)."""

    @abstractmethod
    async def get(self, key: str) -> bytes:
        """Return the bytes stored under ``key``.

        Raises:
            ObjectNotFoundError: when the key does not exist.
        """

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete ``key`` if present (idempotent)."""

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Return True when ``key`` exists."""

    @abstractmethod
    async def signed_url(
        self, key: str, *, expires_seconds: int = 300
    ) -> str:
        """Return a time-limited access URL or token for ``key``."""
