"""Image decoding.

Uses Pillow lazily. When Pillow is unavailable, decoding fails with an honest
unavailable error rather than proceeding with unvalidated bytes.
"""

from __future__ import annotations

from typing import Any

from app.exceptions.validation import ImageDecodeError

_SUPPORTED_FORMATS = {"JPEG", "PNG"}


def _pil():
    try:
        from PIL import Image  # type: ignore

        return Image
    except Exception as exc:  # noqa: BLE001
        raise ImageDecodeError(
            "Image decoding is unavailable: the Pillow dependency is not installed."
        ) from exc


def decode_image(data: bytes) -> Any:
    """Decode image bytes into a Pillow image.

    Raises:
        ImageDecodeError: when decoding fails or the format is unsupported.
    """
    Image = _pil()
    import io

    try:
        with Image.open(io.BytesIO(data)) as img:
            img.load()
            fmt = (img.format or "").upper()
            if fmt not in _SUPPORTED_FORMATS:
                raise ImageDecodeError(
                    f"Unsupported image format: {fmt or 'unknown'}."
                )
            # Return a detached copy so the file handle can close.
            return img.copy()
    except ImageDecodeError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise ImageDecodeError("The provided image could not be decoded.") from exc
