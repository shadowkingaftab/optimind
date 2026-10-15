"""Image metadata extraction.

Extracts only structural metadata needed for validation and persistence.
EXIF and other embedded metadata are intentionally not read or retained.
"""

from __future__ import annotations

from typing import Any

from app.preprocessing.preprocessing_contract import ImageInfo


def extract_metadata(image: Any) -> ImageInfo:
    """Return structural metadata for a decoded image."""
    width, height = image.size
    return ImageInfo(
        width=int(width),
        height=int(height),
        mode=str(image.mode),
        format=str(image.format or "").upper(),
    )


def aspect_ratio(width: int, height: int) -> float:
    if height <= 0:
        return 0.0
    return float(width) / float(height)
