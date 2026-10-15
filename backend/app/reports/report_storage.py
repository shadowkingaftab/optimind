"""Report object storage helpers.

Reports are stored via the configured storage backend under the ``reports``
prefix. Only the storage key is persisted on the report record.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from app.storage import get_storage
from app.storage.file_naming import build_key
from app.utils.hashing import sha256_hex
from app.utils.identifiers import new_uuid_str


@dataclass(frozen=True)
class StoredReport:
    key: str
    size_bytes: int
    checksum_sha256: str


async def store_report(
    *,
    patient_id: str,
    data: bytes,
    media_type: str = "application/pdf",
    extension: str = ".pdf",
) -> StoredReport:
    """Persist report bytes and return their storage descriptor."""
    key = build_key(
        prefix="reports",
        owner_id=str(patient_id),
        extension=extension,
        unique=new_uuid_str(),
    )
    stored = await get_storage().put(key, data, content_type=media_type)
    return StoredReport(
        key=stored.key,
        size_bytes=stored.size_bytes,
        checksum_sha256=stored.checksum_sha256 or sha256_hex(data),
    )
