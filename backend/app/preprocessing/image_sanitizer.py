"""Image sanitization.

Re-encodes decoded pixel data into a clean image, discarding any embedded
metadata (EXIF, ICC profiles, thumbnails, textual chunks). This prevents
hidden payloads and identifying metadata from being stored or forwarded.
"""

from __future__ import annotations

import io
from typing import Any

from app.preprocessing.preprocessing_contract import PreprocessedImage
from app.utils.hashing import sha256_hex

_TARGET_FORMAT = "JPEG"
_TARGET_MEDIA = "image/jpeg"


def sanitize_image(image: Any, *, max_dimension: int | None = None) -> PreprocessedImage:
    """Return a metadata-free, re-encoded JPEG.

    The image is converted to RGB (JPEG has no alpha channel) and re-encoded
    from scratch so no original metadata survives.
    """
    working = image
    if working.mode not in ("RGB", "L"):
        working = working.convert("RGB")

    if max_dimension and max(working.size) > max_dimension:
        working = working.copy()
        working.thumbnail((max_dimension, max_dimension))

    buffer = io.BytesIO()
    working.save(buffer, format=_TARGET_FORMAT, quality=95, optimize=True)
    data = buffer.getvalue()

    width, height = working.size
    return PreprocessedImage(
        data=data,
        media_type=_TARGET_MEDIA,
        width=int(width),
        height=int(height),
        format=_TARGET_FORMAT,
        checksum_sha256=sha256_hex(data),
    )


def encode_png(image: Any) -> PreprocessedImage:
    working = image
    if working.mode not in ("RGB", "RGBA", "L"):
        working = working.convert("RGB")
    buffer = io.BytesIO()
    working.save(buffer, format="PNG", optimize=True)
    data = buffer.getvalue()
    width, height = working.size
    return PreprocessedImage(
        data=data,
        media_type="image/png",
        width=int(width),
        height=int(height),
        format="PNG",
        checksum_sha256=sha256_hex(data),
    )
