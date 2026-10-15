"""Artifact suppression helpers.

Conservative, opt-in operations: zero out non-retinal background outside the
detected region and clip extreme specular highlights. These are heuristics to
reduce nuisance variation; they never synthesise content and must be validated
against the model's preservation requirements. They are disabled by default.
"""

from __future__ import annotations

from typing import Optional

import numpy as np

from .crop_retina import find_retina_bbox

__all__ = ["mask_background", "suppress_highlights"]


def mask_background(
    image: np.ndarray,
    *,
    threshold: int = 7,
    fill_value: int = 0,
) -> np.ndarray:
    """Set pixels outside the detected retinal bounding box to ``fill_value``."""
    bbox = find_retina_bbox(image, threshold=threshold)
    if bbox is None:
        return np.asarray(image).copy()
    left, top, right, bottom = bbox
    out = np.asarray(image).copy()
    out[:top, :] = fill_value
    out[bottom:, :] = fill_value
    out[:, :left] = fill_value
    out[:, right:] = fill_value
    return out


def suppress_highlights(
    image: np.ndarray,
    *,
    percentile: float = 99.5,
    replacement: Optional[float] = None,
) -> np.ndarray:
    """Clip the brightest ``100 - percentile``% of pixels to a ceiling."""
    array = np.asarray(image).astype(np.float32)
    ceiling = float(np.percentile(array, percentile))
    if replacement is not None:
        ceiling = float(replacement)
    clipped = np.minimum(array, ceiling)
    if np.asarray(image).dtype == np.uint8:
        return np.clip(clipped, 0, 255).astype(np.uint8)
    return clipped.astype(np.float32)
