"""Hashing helpers.

Only structural hashes (for integrity and at-rest token derivation) are
provided. Hashes of image bytes for integrity; never for PHI indexing.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Union


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Union[str, Path], *, chunk_size: int = 8192) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()
