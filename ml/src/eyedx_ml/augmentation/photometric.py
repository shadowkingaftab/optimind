"""Photometric augmentations.

Brightness, contrast, gamma and channel jitter. Retinal images are sensitive to
colour and illumination; defaults are deliberately mild and all operations are
opt-in via configuration.
"""

from __future__ import annotations

from typing import Optional, Sequence, Tuple

import numpy as np

__all__ = [
    "adjust_brightness",
    "adjust_contrast",
    "adjust_gamma",
    "channel_jitter",
    "apply_photometric",
]


def _clip_like(original: np.ndarray, result: np.ndarray) -> np.ndarray:
    if original.dtype == np.uint8:
        return np.clip(result, 0, 255).astype(np.uint8)
    return result.astype(np.float32)


def adjust_brightness(
    image: np.ndarray,
    rng: Optional[np.random.Generator] = None,
    *,
    factor: float = 0.1,
    p: float = 0.5,
) -> np.ndarray:
    rng = rng or np.random.default_rng()
    if rng.random() >= p:
        return image
    delta = float(rng.uniform(-factor, factor))
    scale = 255.0 if image.dtype == np.uint8 else 1.0
    return _clip_like(image, image.astype(np.float32) + delta * scale)


def adjust_contrast(
    image: np.ndarray,
    rng: Optional[np.random.Generator] = None,
    *,
    factor: float = 0.1,
    p: float = 0.5,
) -> np.ndarray:
    rng = rng or np.random.default_rng()
    if rng.random() >= p:
        return image
    delta = float(rng.uniform(1.0 - factor, 1.0 + factor))
    mean = float(image.mean())
    return _clip_like(image, (image.astype(np.float32) - mean) * delta + mean)


def adjust_gamma(
    image: np.ndarray,
    rng: Optional[np.random.Generator] = None,
    *,
    gamma_range: Tuple[float, float] = (0.8, 1.2),
    p: float = 0.5,
) -> np.ndarray:
    rng = rng or np.random.default_rng()
    if rng.random() >= p:
        return image
    gamma = float(rng.uniform(*gamma_range))
    array = image.astype(np.float32)
    if image.dtype == np.uint8:
        array = array / 255.0
        return _clip_like(image, np.power(np.clip(array, 0, 1), gamma) * 255.0)
    return np.power(np.clip(array, 0, 1), gamma).astype(np.float32)


def channel_jitter(
    image: np.ndarray,
    rng: Optional[np.random.Generator] = None,
    *,
    factor: float = 0.05,
    p: float = 0.5,
) -> np.ndarray:
    rng = rng or np.random.default_rng()
    if rng.random() >= p or image.ndim != 3:
        return image
    gains = 1.0 + rng.uniform(-factor, factor, size=image.shape[2]).astype(np.float32)
    return _clip_like(image, image.astype(np.float32) * gains.reshape(1, 1, -1))


def apply_photometric(
    image: np.ndarray,
    rng: Optional[np.random.Generator] = None,
    *,
    brightness: float = 0.0,
    contrast: float = 0.0,
    gamma: Optional[Tuple[float, float]] = None,
    jitter: float = 0.0,
) -> np.ndarray:
    rng = rng or np.random.default_rng()
    out = image
    if brightness:
        out = adjust_brightness(out, rng, factor=brightness)
    if contrast:
        out = adjust_contrast(out, rng, factor=contrast)
    if gamma:
        out = adjust_gamma(out, rng, gamma_range=gamma)
    if jitter:
        out = channel_jitter(out, rng, factor=jitter)
    return out
