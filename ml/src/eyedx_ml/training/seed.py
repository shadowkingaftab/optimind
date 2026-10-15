"""Reproducibility helpers for training runs."""

from __future__ import annotations

from typing import Optional

from eyedx_ml.errors import DependencyError
from eyedx_ml.utils.reproducibility import resolve_seed, seed_everything

__all__ = ["configure_reproducibility", "TRAIN_SEED_DEFAULT"]

TRAIN_SEED_DEFAULT = 42


def configure_reproducibility(
    seed: Optional[int] = None,
    *,
    deterministic: bool = True,
    benchmark: bool = False,
):
    """Seed python/numpy/torch and configure cuDNN determinism.

    Returns the resolved :class:`~eyedx_ml.utils.reproducibility.SeedState`.
    """
    resolved = resolve_seed(seed, default=TRAIN_SEED_DEFAULT)
    state = seed_everything(resolved)
    try:
        import torch

        if torch.backends.cudnn is not None:
            torch.backends.cudnn.deterministic = bool(deterministic)
            torch.backends.cudnn.benchmark = bool(benchmark)
    except Exception:
        # torch may be absent for CPU-only tooling; seeding python/numpy stands.
        pass
    return state
