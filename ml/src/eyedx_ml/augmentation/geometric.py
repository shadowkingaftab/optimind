"""Geometric augmentations.

Flip, rotate and random-crop operations applied to NumPy arrays. Each function
takes an explicit ``numpy.random.Generator`` so runs are reproducible. Retinal
images are approximately rotation-sensitive; use small angles and avoid
vertical flips unless validated.
"""

from __future__ import annotations

from typing import Optional, Tuple

import numpy as np

__all__ = [
    "horizontal_flip",
    "vertical_flip",
    "rotate90",
    "random_rotate",
    "random_crop",
    "apply_geometric",
]


def horizontal_flip(image: np.ndarray, rng: Optional[np.random.Generator] = None, *, p: float = 0.5) -> np.ndarray:
    rng = rng or np.random.default_rng()
    return np.ascontiguousarray(image[:, ::-1]) if rng.random() < p else image


def vertical_flip(image: np.ndarray, rng: Optional[np.random.Generator] = None, *, p: float = 0.5) -> np.ndarray:
    rng = rng or np.random.default_rng()
    return np.ascontiguousarray(image[::-1, :]) if rng.random() < p else image


def rotate90(image: np.ndarray, rng: Optional[np.random.Generator] = None, *, p: float = 0.5) -> np.ndarray:
    rng = rng or np.random.default_rng()
    if rng.random() >= p:
        return image
    k = int(rng.integers(0, 4))
    return np.ascontiguousarray(np.rot90(image, k))


def random_rotate(
    image: np.ndarray,
    rng: Optional[np.random.Generator] = None,
    *,
    max_angle: float = 15.0,
    p: float = 0.5,
    fill_value: int = 0,
) -> np.ndarray:
    rng = rng or np.random.default_rng()
    if rng.random() >= p:
        return image
    angle = float(rng.uniform(-max_angle, max_angle))
    try:  # pragma: no cover - optional dependency
        from PIL import Image
    except Exception:
        return image
    array = image
    if array.dtype != np.uint8:
        array = np.clip(array, 0, 255).astype(np.uint8)
        cast_back = True
    else:
        cast_back = False
    pil = Image.fromarray(array)
    rotated = pil.rotate(angle, resample=Image.Resampling.BILINEAR, fillcolor=fill_value)
    result = np.asarray(rotated)
    if cast_back:
        return result.astype(np.float32)
    return result


def random_crop(
    image: np.ndarray,
    rng: Optional[np.random.Generator] = None,
    *,
    scale: Tuple[float, float] = (0.8, 1.0),
    p: float = 0.5,
) -> np.ndarray:
    rng = rng or np.random.default_rng()
    if rng.random() >= p:
        return image
    h, w = image.shape[:2]
    factor = float(rng.uniform(scale[0], scale[1]))
    crop_h, crop_w = max(1, int(h * factor)), max(1, int(w * factor))
    top = int(rng.integers(0, max(1, h - crop_h + 1)))
    left = int(rng.integers(0, max(1, w - crop_w + 1)))
    return np.ascontiguousarray(image[top : top + crop_h, left : left + crop_w])


def apply_geometric(
    image: np.ndarray,
    rng: Optional[np.random.Generator] = None,
    *,
    hflip_p: float = 0.5,
    vflip_p: float = 0.0,
    rotate90_p: float = 0.0,
    max_angle: float = 0.0,
) -> np.ndarray:
    rng = rng or np.random.default_rng()
    out = image
    if hflip_p:
        out = horizontal_flip(out, rng, p=hflip_p)
    if vflip_p:
        out = vertical_flip(out, rng, p=vflip_p)
    if rotate90_p:
        out = rotate90(out, rng, p=rotate90_p)
    if max_angle > 0:
        out = random_rotate(out, rng, max_angle=max_angle, p=1.0)
    return out
