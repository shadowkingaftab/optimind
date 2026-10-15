"""Upload file validation.

Validates extension, declared media type, byte size and magic bytes before
any decode is attempted. Rejections carry honest, non-clinical reasons.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.core.constants import ALLOWED_IMAGE_EXTENSIONS, ALLOWED_IMAGE_MEDIA_TYPES
from app.exceptions.validation import (
    ImageTooLargeError,
    RequestValidationError,
    UnsupportedImageFormatError,
)
from app.utils.file_utils import get_extension, guess_media_type

_MAGIC_SIGNATURES: dict[str, tuple[bytes, ...]] = {
    ".jpg": (b"\xff\xd8\xff",),
    ".jpeg": (b"\xff\xd8\xff",),
    ".png": (b"\x89PNG\r\n\x1a\n",),
}


@dataclass(frozen=True)
class ValidatedUpload:
    extension: str
    media_type: str
    size_bytes: int


def validate_upload(
    *,
    filename: str | None,
    content_type: str | None,
    data: bytes,
    allowed_extensions: frozenset[str] | None = None,
    allowed_media_types: frozenset[str] | None = None,
    max_bytes: int = 0,
) -> ValidatedUpload:
    """Validate an uploaded image payload.

    Raises:
        RequestValidationError: missing/empty payload.
        UnsupportedImageFormatError: extension/media type/signature mismatch.
        ImageTooLargeError: payload exceeds the configured maximum.
    """
    exts = allowed_extensions or ALLOWED_IMAGE_EXTENSIONS
    media = allowed_media_types or ALLOWED_IMAGE_MEDIA_TYPES

    if not data:
        raise RequestValidationError("The uploaded file is empty.")

    ext = get_extension(filename)
    if ext not in exts:
        raise UnsupportedImageFormatError(
            "Unsupported image extension. Allowed: "
            + ", ".join(sorted(exts))
        )

    declared = (content_type or "").split(";")[0].strip().lower()
    resolved_media = declared or guess_media_type(ext)
    if resolved_media not in media:
        raise UnsupportedImageFormatError(
            "Unsupported media type. Allowed: " + ", ".join(sorted(media))
        )

    if max_bytes and len(data) > max_bytes:
        raise ImageTooLargeError(
            f"The uploaded file exceeds the {max_bytes} byte limit."
        )

    signatures = _MAGIC_SIGNATURES.get(ext, ())
    if signatures and not any(data.startswith(sig) for sig in signatures):
        raise UnsupportedImageFormatError(
            "The file content does not match its declared image format."
        )

    return ValidatedUpload(
        extension=ext, media_type=resolved_media, size_bytes=len(data)
    )
