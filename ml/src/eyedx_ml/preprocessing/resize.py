"""Resize and letterbox operations.

Accepts NumPy arrays (H, W, C) or PIL images inside a callable. Resizing can
preserve aspect ratio and letterbox with padding, which is preferred for retinal
fundus images to avoid geometric distortion.
"""

from __future__ import annotations

from typing import Optional, Tuple, Union

import numpy as np

__all__ = ["resize_image", "letterbox"]

_RESAMPLE = {
    "nearest": "NEAREST",
    "bilinear": "BILINEAR",
    "bicubic": "BICUBIC",
    "lanczos": "LANCZOS",
}


def _require_pillow():
    try:  # pragma: no cover - optional dependency
        from PIL import Image
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("Pillow is required for resize operations") from exc
    return Image


def _to_pil(image: np.ndarray):
    Image = _require_pillow()
    array = image
    if array.dtype != np.uint8:
        array = np.clip(array, 0, 255).astype(np.uint8)
    return Image.fromarray(array)


def resize_image(
    image: np.ndarray,
    size: Tuple[int, int],
    *,
    keep_aspect: bool = False,
    resample: str = "bilinear",
    pad_value: int = 0,
) -> np.ndarray:
    """Resize to ``size = (width, height)``.

    When ``keep_aspect`` is true the image is scaled to fit and padded.
    """
    if keep_aspect:
        return letterbox(image, size, pad_value=pad_value, resample=resample)
    Image = _require_pillow()
    method = getattr(Image.Resampling, _RESAMPLE.get(resample, "BILINEAR"))
    pil = _to_pil(image)
    resized = pil.resize(size, method)
    return np.asarray(resized)


def letterbox(
    image: np.ndarray,
    size: Tuple[int, int],
    *,
    pad_value: int = 0,
    resample: str = "bilinear",
) -> np.ndarray:
    """Scale to fit inside ``size`` and pad to exactly ``size``."""
    Image = _require_pillow()
    target_w, target_h = size
    h, w = image.shape[:2]
    if h == 0 or w == 0:
        raise ValueError("cannot resize an empty image")
    scale = min(target_w / w, target_h / h)
    new_w, new_h = max(1, int(round(w * scale))), max(1, int(round(h * scale)))
    method = getattr(Image.Resampling, _RESAMPLE.get(resample, "BILINEAR"))
    resized = np.asarray(_to_pil(image).resize((new_w, new_h), method))

    channels = resized.shape[2] if resized.ndim == 3 else 1
    pad_shape = (target_h, target_w) + ((channels,) if resized.ndim == 3 else ())
    canvas = np.full(pad_shape, pad_value, dtype=resized.dtype)
    top = (target_h - new_h) // 2
    left = (target_w - new_w) // 2
    canvas[top : top + new_h, left : left + new_w] = resized
    return canvas
