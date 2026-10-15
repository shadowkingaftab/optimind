"""Reproducibility helpers.

Seeding is centralised here so every entrypoint (ingest, split, train) applies
the same policy. Heavy frameworks (torch, tensorflow) are imported lazily so
data-only environments do not need them.
"""

from __future__ import annotations

import os
import random
from dataclasses import dataclass
from typing import Any, Dict, Optional

import numpy as np

__all__ = ["SeedState", "seed_everything", "DEFAULT_SEED"]

DEFAULT_SEED = 42


@dataclass(frozen=True)
class SeedState:
    """A record of what was seeded, for provenance."""

    seed: int
    numpy_version: str
    frameworks: Dict[str, bool]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "seed": self.seed,
            "numpy_version": self.numpy_version,
            "frameworks": dict(self.frameworks),
        }


def seed_everything(
    seed: int = DEFAULT_SEED,
    *,
    deterministic_torch: bool = True,
) -> SeedState:
    """Seed Python, NumPy and (if installed) PyTorch.

    Returns a :class:`SeedState` describing the frameworks detected. Never
    raises when an optional framework is missing.
    """
    if seed < 0:
        raise ValueError("seed must be non-negative")

    os.environ.setdefault("PYTHONHASHSEED", str(seed))
    random.seed(seed)
    np.random.seed(seed)

    frameworks: Dict[str, bool] = {"torch": False, "tensorflow": False}

    try:  # pragma: no cover - optional dependency
        import torch

        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
        if deterministic_torch:
            try:
                torch.use_deterministic_algorithms(True, warn_only=True)
            except Exception:
                pass
        frameworks["torch"] = True
    except Exception:
        pass

    try:  # pragma: no cover - optional dependency
        import tensorflow as tf

        tf.random.set_seed(seed)
        frameworks["tensorflow"] = True
    except Exception:
        pass

    return SeedState(
        seed=seed, numpy_version=np.__version__, frameworks=frameworks
    )


def resolve_seed(explicit: Optional[int] = None) -> int:
    """Resolve a seed from an explicit value or the ``EYEDX_SEED`` env var."""
    if explicit is not None:
        return int(explicit)
    raw = os.environ.get("EYEDX_SEED")
    if raw is None or not raw.strip():
        return DEFAULT_SEED
    return int(raw)
