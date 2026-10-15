"""Model architectures, backbones, layers, losses and ensembles.

Submodules with heavy dependencies (torch/torchvision) are imported lazily inside
their builders, so importing :mod:`eyedx_ml.models` stays lightweight.
"""

from __future__ import annotations

from .model_config import ARCHITECTURES, ModelConfig, load_model_config
from .model_factory import build_model, build_model_from_file, describe_model

__all__ = [
    "ARCHITECTURES",
    "ModelConfig",
    "load_model_config",
    "build_model",
    "build_model_from_file",
    "describe_model",
]
