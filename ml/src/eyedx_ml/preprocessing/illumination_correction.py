"""Illumination correction.

Flattens uneven lighting by dividing out a heavily blurred version of the
image (a cheap background estimate) and rescaling to the original range.
Heuristic and reversible in intent; it never adds information.
"""

from __future__ import annotations

from typing import Optional

import numpy as np

__all__ = ["correct_illumination", "estimate_background"]


def estimate_background(image: np.ndarray, *, radius: int = 25) -> np.ndarray:
    """Estimate a smooth background via a box blur over a downsampled image."""
    array = np.asarray(image).astype(np.float32)
    h, w = array.shape[:2]
    step = max(1, radius)
    small = array[::step, ::step]
    if small.shape[0] < 2 or small.shape[1] < 2:
        return array
    # Iterative box blur as a cheap Gaussian approximation.
    background = small
    for _ in range(3):
        padded = np.pad(background, ((1, 1), (1, 1)) + ((0, 0),) * (background.ndim - 2), mode="edge")
        background = (
            padded[:-2, 1:-1]
            + padded[2:, 1:-1]
            + padded[1:-1, :-2]
            + padded[1:-1, 2:]
            + padded[1:-1, 1:-1]
        ) / 5.0
    from .resize import resize_image

    background_full = resize_image(
        np.clip(background, 0, 255).astype(np.uint8), (w, h)
    ).astype(np.float32)
    return background_full


def correct_illumination(
    image: np.ndarray,
    *,
    radius: int = 25,
    strength: float = 1.0,
    eps: float = 1e-3,
) -> np.ndarray:
    """Divide out background illumination, blending by ``strength`` in [0,1]."""
    array = np.asarray(image)
    work = array.astype(np.float32)
    background = estimate_background(array, radius=radius)
    if background.ndim == 2 and work.ndim == 3:
        background = background[..., None]
    corrected = work / np.maximum(background, eps) * (background.mean() if background.size else 1.0)
    strength = float(np.clip(strength, 0.0, 1.0))
    blended = work * (1.0 - strength) + corrected * strength
    if array.dtype == np.uint8:
        return np.clip(blended, 0, 255).astype(np.uint8)
    return blended.astype(np.float32)
