"""Colour correction.

Implements inert, well-understood colour transforms: grey-world white balancing
and per-channel standardisation. No colour transform is applied by default;
callers must opt in, since colour shifts can remove clinically meaningful cues.
"""

from __future__ import annotations

from typing import Optional, Sequence

import numpy as np

__all__ = ["gray_world", "standardize_channels", "apply_channel_gains"]


def apply_channel_gains(image: np.ndarray, gains: Sequence[float]) -> np.ndarray:
    array = np.asarray(image).astype(np.float32)
    if array.ndim != 3:
        raise ValueError("channel gains require a colour image")
    gains_arr = np.asarray(gains, dtype=np.float32).reshape(1, 1, -1)
    corrected = array * gains_arr
    if np.asarray(image).dtype == np.uint8:
        return np.clip(corrected, 0, 255).astype(np.uint8)
    return corrected.astype(np.float32)


def gray_world(image: np.ndarray, *, eps: float = 1e-6) -> np.ndarray:
    """Grey-world white balance: equalise per-channel means."""
    array = np.asarray(image).astype(np.float32)
    if array.ndim != 3:
        return array.astype(np.asarray(image).dtype)
    means = array.reshape(-1, array.shape[2]).mean(axis=0)
    target = float(means.mean())
    gains = target / np.maximum(means, eps)
    return apply_channel_gains(array, gains)


def standardize_channels(
    image: np.ndarray,
    *,
    mean: Optional[Sequence[float]] = None,
    std: Optional[Sequence[float]] = None,
) -> np.ndarray:
    """Per-channel standardisation using supplied or per-image statistics."""
    array = np.asarray(image).astype(np.float32)
    if array.ndim == 2:
        array = array[..., None]
    if mean is None or std is None:
        m = array.mean(axis=(0, 1), keepdims=True)
        s = array.std(axis=(0, 1), keepdims=True)
    else:
        m = np.asarray(mean, dtype=np.float32).reshape(1, 1, -1)
        s = np.asarray(std, dtype=np.float32).reshape(1, 1, -1)
    return (array - m) / np.maximum(s, 1e-6)
