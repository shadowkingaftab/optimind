"""File hashing utilities.

Used for duplicate detection, integrity checks and manifest checksums. Hashing
never logs file contents and never follows symlinks outside a root by default.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Optional, Union

__all__ = ["sha256_bytes", "sha256_file", "file_size"]

_CHUNK = 1024 * 1024


def sha256_bytes(data: bytes) -> str:
    """Return the hex SHA-256 of ``data``."""
    return hashlib.sha256(data).hexdigest()


def sha256_file(
    path: Union[str, Path], *, chunk_size: int = _CHUNK
) -> str:
    """Return the hex SHA-256 of a file, streaming it in chunks."""
    digest = hashlib.sha256()
    file_path = Path(path)
    if not file_path.is_file():
        raise FileNotFoundError(f"file not found: {file_path.name}")
    with file_path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_size(path: Union[str, Path]) -> int:
    """Return the size in bytes of ``path``."""
    return Path(path).stat().st_size
