"""Augmentation factory.

Builds a seeded per-image augmentation callable from configuration, and resolves
batch mixers (MixUp/CutMix) by name. Augmentation is training-only; callers must
not attach it to validation/test datasets.
"""

from __future__ import annotations

from typing import Any, Callable, Mapping, Optional

import numpy as np

from .cutmix import cutmix_batch
from .geometric import apply_geometric
from .mixup import mixup_batch
from .noise import apply_noise
from .photometric import apply_photometric

__all__ = ["AugmentationError", "build_augmentation", "build_mixer"]


class AugmentationError(ValueError):
    """Raised for unknown augmentation options."""


def build_augmentation(
    config: Optional[Mapping[str, Any]] = None,
    *,
    seed: Optional[int] = None,
) -> Callable[[np.ndarray], np.ndarray]:
    """Return a callable applying the configured augmentations to one image."""
    config = dict(config or {})
    seed_value = int(config.get("seed", seed if seed is not None else 42))
    geometric = dict(config.get("geometric") or {})
    photometric = dict(config.get("photometric") or {})
    noise = dict(config.get("noise") or {})
    rng = np.random.default_rng(seed_value)

    def augment(image: np.ndarray) -> np.ndarray:
        out = image
        if geometric:
            out = apply_geometric(out, rng, **geometric)
        if photometric:
            gamma = photometric.pop("gamma", None) if "gamma" in photometric else None
            out = apply_photometric(out, rng, gamma=gamma, **photometric)
        if noise:
            out = apply_noise(out, rng, **noise)
        return out

    return augment


def build_mixer(
    name: str,
    *,
    alpha: float = 0.2,
) -> Callable[[Any, Any, np.random.Generator], Any]:
    """Return a batch mixer callable for ``name`` in {mixup, cutmix, none}."""
    lowered = name.lower()
    if lowered in ("none", "off", ""):
        def identity(x, y, rng):  # pragma: no cover - trivial
            return x, y, 1.0

        return identity
    if lowered == "mixup":
        return lambda x, y, rng: mixup_batch(x, y, rng=rng, alpha=alpha)
    if lowered == "cutmix":
        return lambda x, y, rng: cutmix_batch(x, y, rng=rng, alpha=alpha)
    raise AugmentationError(f"unknown mixer: {name}")
