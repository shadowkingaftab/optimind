"""MixUp sample mixing.

Mixes pairs of images and their targets with a lambda drawn from a Beta
distribution. Works on NumPy arrays and PyTorch tensors alike through duck
typing. Applied only during training and only per batch.
"""

from __future__ import annotations

from typing import Tuple

import numpy as np

__all__ = ["sample_lambda", "mixup_batch"]


def sample_lambda(rng: np.random.Generator, alpha: float) -> float:
    if alpha <= 0:
        return 1.0
    return float(rng.beta(alpha, alpha))


def mixup_batch(
    x,
    y,
    *,
    rng: np.random.Generator,
    alpha: float = 0.2,
) -> Tuple[object, object, float]:
    """Return ``(mixed_x, mixed_y, lam)``.

    ``x`` is ``(B, ...)``; ``y`` is ``(B, ...)`` numeric targets (multi-hot
    labels, scalars or one-hot vectors).
    """
    if alpha <= 0:
        return x, y, 1.0
    lam = sample_lambda(rng, alpha)
    index = rng.permutation(int(len(x)))
    mixed_x = x * lam + x[index] * (1.0 - lam)
    mixed_y = y * lam + y[index] * (1.0 - lam)
    return mixed_x, mixed_y, lam
