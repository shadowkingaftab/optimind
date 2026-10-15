"""Explainability methods.

Explanations support review and safety oversight. They are not diagnostic and
must be presented as screening assistance only.
"""

from __future__ import annotations

from .attention_rollout import attention_rollout
from .explanation_validator import (
    deletion_score,
    insertion_score,
    validate_heatmap,
)
from .gradcam import GradCAM
from .heatmap_utils import (
    normalize_heatmap,
    overlay_heatmap,
    resize_heatmap,
    save_heatmap,
)
from .integrated_gradients import integrated_gradients
from .occlusion import occlusion_sensitivity

__all__ = [
    "GradCAM",
    "integrated_gradients",
    "occlusion_sensitivity",
    "attention_rollout",
    "normalize_heatmap",
    "resize_heatmap",
    "overlay_heatmap",
    "save_heatmap",
    "validate_heatmap",
    "deletion_score",
    "insertion_score",
]
