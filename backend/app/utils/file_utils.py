"""Filesystem and filename helpers.

Filenames are normalised and restricted to safe characters to avoid path
traversal. Only the storage key is written to the database.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

_ALLOWED_SAFE = re.compile(r"[^A-Za-z0-9._-]+")


def get_extension(filename: str | None) -> str:
    if not filename:
        return ""
    ext = os.path.splitext(filename)[1].lower()
    return ext


def normalize_extension(ext: str | None) -> str:
    if not ext:
        return ""
    e = ext.lower()
    return f".{e.lstrip('.')}"

def safe_filename(filename: str, max_len: int = 128) -> str:
    name = Path(filename).name
    base, ext = os.path.splitext(name)
    base = _ALLOWED_SAFE.sub("_", base).strip("._-") or "file"
    ext = ext.lower()
    if len(base) + len(ext) > max_len:
        base = base[: max_len - len(ext)]
    return f"{base}{ext}"


def guess_media_type(ext: str | None) -> str:
    e = normalize_extension(ext)
    if e in (".jpg", ".jpeg"):
        return "image/jpeg"
    if e == ".png":
        return "image/png"
    if e == ".pdf":
        return "application/pdf"
    return "application/octet-stream"


def human_size(num_bytes: int) -> str:
    step = 1024.0
    units = ("B", "KB", "MB", "GB", "TB")
    if num_bytes < 0:
        num_bytes = 0
    size = float(num_bytes)
    for unit in units:
        if size < step:
            return f"{size:3.1f} {unit}"
        size /= step
    return f"{size:.1f} PB"
