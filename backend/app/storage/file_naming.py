"""Deterministic storage key generation.

Keys are opaque, namespaced and sharded by a hash prefix to bound directory
sizes. They never contain patient identifiers or original filenames.
"""

from __future__ import annotations

import hashlib
from datetime import datetime

from app.utils.datetime import utcnow


def _shard(seed: str) -> str:
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    return digest[:2]


def build_key(
    *,
    prefix: str,
    owner_id: str,
    extension: str,
    unique: str,
    when: datetime | None = None,
) -> str:
    """Build a storage key like ``images/ab/<owner>/<year>/<unique>.jpg``."""
    moment = when or utcnow()
    ext = extension if extension.startswith(".") else f".{extension}"
    ext = ext.lower()
    shard = _shard(f"{owner_id}{unique}")
    return f"{prefix}/{shard}/{owner_id}/{moment.year}/{unique}{ext}"


def quarantine_key(*, unique: str, extension: str = ".bin") -> str:
    ext = extension if extension.startswith(".") else f".{extension}"
    return f"quarantine/{_shard(unique)}/{unique}{ext.lower()}"
