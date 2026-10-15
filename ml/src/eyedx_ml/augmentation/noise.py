"""Noise and blur augmentations.

Additive Gaussian noise, salt-and-pepper and mild blur, all seeded and opt-in.
Noise strength defaults are conservative; excessive noise can mimic pathology
and should be validated.
"""

from __future__ import annotations

from typing import Optional, Tuple

import numpy as np

__all__ = ["gaussian_noise", "salt_pepper", "gaussian_blur", "apply_noise"]


def _clip_like(original: np.ndarray, result: np.ndarray) -> np.ndarray:
    if original.dtype == np.uint8:
        return np.clip(result, 0, 255).astype(np.uint8)
    return result.astype(np.float32)


def gaussian_noise(
    image: np.ndarray,
    rng: Optional[np.random.Generator] = None,
    *,
    sigma: float = 0.02,
    p: float = 0.5,
) -> np.ndarray:
    rng = rng or np.random.default_rng()
    if rng.random() >= p:
        return image
    scale = 255.0 if image.dtype == np.uint8 else 1.0
    noise = rng.normal(0.0, sigma * scale, size=image.shape).astype(np.float32)
    return _clip_like(image, image.astype(np.float32) + noise)


def salt_pepper(
    image: np.ndarray,
    rng: Optional[np.random.Generator] = None,
    *,
    amount: float = 0.005,
    p: float = 0.5,
) -> np.ndarray:
    rng = rng or np.random.default_rng()
    if rng.random() >= p:
        return image
    out = image.astype(np.float32).copy()
    high = 255.0 if image.dtype == np.uint8 else 1.0
    mask = rng.random(image.shape[:2])
    out[mask < amount / 2] = 0.0
    out[(mask >= amount / 2) & (mask < amount)] = high
    return _clip_like(image, out)


def gaussian_blur(
    image: np.ndarray,
    rng: Optional[np.random.Generator] = None,
    *,
    radius_range: Tuple[float, float] = (0.3, 1.2),
    p: float = 0.5,
) -> np.ndarray:
    rng = rng or np.random.default_rng()
    if rng.random() >= p:
        return image
    try:  # pragma: no cover - optional dependency
        from PIL import Image, ImageFilter
    except Exception:
        return image
    radius = float(rng.uniform(*radius_range))
    array = image
    if array.dtype != np.uint8:
        array = np.clip(array, 0, 255).astype(np.uint8)
        cast_back = True
    else:
        cast_back = False
    blurred = Image.fromarray(array).filter(ImageFilter.GaussianBlur(radius=radius))
    result = np.asarray(blurred)
    return result.astype(np.float32) if cast_back else result


def apply_noise(
    image: np.ndarray,
    rng: Optional[np.random.Generator] = None,
    *,
    gaussian_sigma: float = 0.0,
    blur_radius: Optional[Tuple[float, float]] = None,
    salt_pepper_amount: float = 0.0,
) -> np.ndarray:
    rng = rng or np.random.default_rng()
    out = image
    if gaussian_sigma:
        out = gaussian_noise(out, rng, sigma=gaussian_sigma)
    if salt_pepper_amount:
        out = salt_pepper(out, rng, amount=salt_pepper_amount)
    if blur_radius:
        out = gaussian_blur(out, rng, radius_range=blur_radius)
    return out
