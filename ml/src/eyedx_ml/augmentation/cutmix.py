"""CutMix sample mixing.

Pastes a random rectangle of one sample over another and mixes targets
proportionally to the replaced area. Works on NumPy arrays and PyTorch tensors
through duck typing; targets must be numeric (multi-hot or scalar).
"""

from __future__ import annotations

from typing import Tuple

import numpy as np

__all__ = ["rand_bbox", "cutmix_batch"]


def _channel_first(x) -> bool:
    try:
        channels = int(x.shape[1])
        height_or_channels = int(x.shape[2]) if len(x.shape) > 2 else None
    except Exception:
        return True
    if height_or_channels is None:
        return True
    return channels <= 32


def rand_bbox(size, lam: float, rng: np.random.Generator) -> Tuple[int, int, int, int]:
    """Sample a bounding box ``(y1, x1, y2, x2)`` with the given cut ratio."""
    if _channel_first(size):
        height, width = int(size[2]), int(size[3])
    else:
        height, width = int(size[1]), int(size[2])
    cut = float(np.sqrt(1.0 - lam)) * height * width
    cy = int(rng.uniform(0, height))
    cx = int(rng.uniform(0, width))
    y1 = int(np.clip(cy - cut / (2 * height), 0, height))
    x1 = int(np.clip(cx - cut / (2 * width), 0, width))
    y2 = int(np.clip(cy + cut / (2 * height), 0, height))
    x2 = int(np.clip(cx + cut / (2 * width), 0, width))
    return y1, x1, y2, x2


def cutmix_batch(
    x,
    y,
    *,
    rng: np.random.Generator,
    alpha: float = 1.0,
) -> Tuple[object, object, float]:
    """Return ``(mixed_x, mixed_y, lam)`` after a CutMix swap."""
    if alpha <= 0:
        return x, y, 1.0
    lam = float(rng.beta(alpha, alpha))
    index = rng.permutation(int(len(x)))
    y1, x1, y2, x2 = rand_bbox(x.shape, lam, rng)

    if _channel_first(x):
        height, width = int(x.shape[2]), int(x.shape[3])
        mixed_x = x.copy() if hasattr(x, "copy") else x
        mixed_x[:, :, y1:y2, x1:x2] = x[index][:, :, y1:y2, x1:x2]
    else:
        height, width = int(x.shape[1]), int(x.shape[2])
        mixed_x = x.copy() if hasattr(x, "copy") else x
        mixed_x[:, y1:y2, x1:x2, :] = x[index][:, y1:y2, x1:x2, :]

    box_area = max(0, (y2 - y1)) * max(0, (x2 - x1))
    total = max(1, height * width)
    lam_adjusted = float(1.0 - box_area / float(total))
    mixed_y = y * lam_adjusted + y[index] * (1.0 - lam_adjusted)
    return mixed_x, mixed_y, lam_adjusted
