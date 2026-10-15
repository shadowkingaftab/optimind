"""Local filesystem storage backend.

All keys are resolved beneath a configured base path. Any resolved path that
escapes the base is rejected to prevent directory traversal.
"""

from __future__ import annotations

import asyncio
import os
from pathlib import Path

from app.exceptions.storage import ObjectNotFoundError, StorageError
from app.storage.signed_urls import sign_token
from app.storage.storage_interface import StorageBackend, StoredObject
from app.utils.hashing import sha256_hex


class LocalStorage(StorageBackend):
    """Filesystem-backed storage rooted at ``base_path``."""

    def __init__(self, base_path: str, *, signing_secret: str) -> None:
        self._base = Path(base_path).resolve()
        self._secret = signing_secret
        self._base.mkdir(parents=True, exist_ok=True)

    def _resolve(self, key: str) -> Path:
        candidate = (self._base / key).resolve()
        if self._base != candidate and self._base not in candidate.parents:
            raise StorageError("Invalid storage key.")
        return candidate

    async def put(
        self,
        key: str,
        data: bytes,
        *,
        content_type: str = "application/octet-stream",
    ) -> StoredObject:
        path = self._resolve(key)
        path.parent.mkdir(parents=True, exist_ok=True)

        def _write() -> None:
            tmp = path.with_suffix(path.suffix + ".tmp")
            with open(tmp, "wb") as fh:
                fh.write(data)
                fh.flush()
                os.fsync(fh.fileno())
            os.replace(tmp, path)

        await asyncio.to_thread(_write)
        return StoredObject(key=key, size_bytes=len(data), checksum_sha256=sha256_hex(data))

    async def get(self, key: str) -> bytes:
        path = self._resolve(key)

        def _read() -> bytes:
            if not path.is_file():
                raise ObjectNotFoundError()
            with open(path, "rb") as fh:
                return fh.read()

        return await asyncio.to_thread(_read)

    async def delete(self, key: str) -> None:
        path = self._resolve(key)

        def _delete() -> None:
            try:
                path.unlink()
            except FileNotFoundError:
                return

        await asyncio.to_thread(_delete)

    async def exists(self, key: str) -> bool:
        path = self._resolve(key)
        return path.is_file()

    async def signed_url(self, key: str, *, expires_seconds: int = 300) -> str:
        token = sign_token(key, secret=self._secret, expires_seconds=expires_seconds)
        return f"/api/v1/files/{token}"
