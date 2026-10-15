"""Retina cropping and border removal.

Detects the circular fundus region by thresholding non-black pixels and crops to
its bounding box, optionally with a margin. This is a geometric heuristic, not a
clinical segmentation; it is safe (returns the input unchanged when detection
fails) and never fabricates regions.
"""

from __future__ import annotations

from typing import Optional, Tuple

import numpy as np

__all__ = ["find_retina_bbox", "crop_retina", "center_crop"]

BBox = Tuple[int, int, int, int]  # left, top, right, bottom


def _grayscale(image: np.ndarray) -> np.ndarray:
    array = np.asarray(image).astype(np.float32)
    if array.ndim == 2:
        return array
    return array[..., :3].mean(axis=2)


def find_retina_bbox(
    image: np.ndarray,
    *,
    threshold: int = 7,
    min_area_ratio: float = 0.02,
) -> Optional[BBox]:
    """Return the bounding box of non-black pixels, or ``None`` if too small."""
    gray = _grayscale(image)
    mask = gray > threshold
    ys, xs = np.where(mask)
    if xs.size == 0:
        return None
    left, right = int(xs.min()), int(xs.max()) + 1
    top, bottom = int(ys.min()), int(ys.max()) + 1
    area_ratio = (right - left) * (bottom - top) / float(gray.shape[0] * gray.shape[1])
    if area_ratio < min_area_ratio:
        return None
    return left, top, right, bottom


def crop_retina(
    image: np.ndarray,
    *,
    threshold: int = 7,
    margin_ratio: float = 0.0,
    target_size: Optional[Tuple[int, int]] = None,
) -> np.ndarray:
    """Crop to the detected retina region; returns input when detection fails."""
    bbox = find_retina_bbox(image, threshold=threshold)
    if bbox is None:
        cropped = image
    else:
        left, top, right, bottom = bbox
        h, w = image.shape[:2]
        margin_x = int((right - left) * margin_ratio)
        margin_y = int((bottom - top) * margin_ratio)
        left = max(0, left - margin_x)
        top = max(0, top - margin_y)
        right = min(w, right + margin_x)
        bottom = min(h, bottom + margin_y)
        cropped = image[top:bottom, left:right]

    if target_size is not None:
        from .resize import resize_image

        cropped = resize_image(cropped, target_size)
    return cropped


def center_crop(image: np.ndarray, size: Tuple[int, int]) -> np.ndarray:
    """Crop the largest centered region of the given ``(width, height)``."""
    target_w, target_h = size
    h, w = image.shape[:2]
    if target_w > w or target_h > h:
        return image
    left = (w - target_w) // 2
    top = (h - target_h) // 2
    return image[top : top + target_h, left : left + target_w]
