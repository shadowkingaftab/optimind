"""Intensity normalisation.

Converts images to float and applies simple per-channel standardisation. Mean
and standard deviation are configuration inputs; defaults are placeholders that
must be computed from the training split (INPUT_REQUIRED until then).
"""

from __future__ import annotations

from typing import Optional, Sequence, Tuple

import numpy as np

__all__ = ["to_float", "normalize", "Normalize"]

# Placeholders only. Real values must be derived from the training split.
IMAGENET_MEAN: Tuple[float, float, float] = (0.485, 0.456, 0.406)
IMAGENET_STD: Tuple[float, float, float] = (0.229, 0.224, 0.225)


def to_float(image: np.ndarray, *, scale: bool = True) -> np.ndarray:
    """Convert to float32; scales uint8 [0,255] to [0,1] when requested."""
    array = np.asarray(image)
    if scale and array.dtype == np.uint8:
        return array.astype(np.float32) / 255.0
    return array.astype(np.float32)


def normalize(
    image: np.ndarray,
    *,
    mean: Optional[Sequence[float]] = None,
    std: Optional[Sequence[float]] = None,
    eps: float = 1e-6,
) -> np.ndarray:
    """Standardise channels: ``(x - mean) / std``.

    When ``mean``/``std`` are omitted, per-image mean and std are used
    (instance normalisation), which is stable when dataset statistics are not
    yet available.
    """
    array = to_float(image)
    if array.ndim == 2:
        array = array[..., None]

    if mean is None or std is None:
        m = array.mean(axis=(0, 1), keepdims=True)
        s = array.std(axis=(0, 1), keepdims=True)
    else:
        m = np.asarray(mean, dtype=np.float32).reshape(1, 1, -1)
        s = np.asarray(std, dtype=np.float32).reshape(1, 1, -1)
    return ((array - m) / np.maximum(s, eps)).astype(np.float32)


class Normalize:
    """Callable wrapper around :func:`normalize` for use in a pipeline."""

    def __init__(
        self,
        mean: Optional[Sequence[float]] = None,
        std: Optional[Sequence[float]] = None,
        *,
        scale: bool = True,
        eps: float = 1e-6,
    ) -> None:
        self.mean = mean
        self.std = std
        self.scale = scale
        self.eps = eps

    def __call__(self, image: np.ndarray) -> np.ndarray:
        array = to_float(image, scale=self.scale)
        return normalize(array, mean=self.mean, std=self.std, eps=self.eps)
