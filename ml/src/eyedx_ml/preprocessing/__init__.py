"""Deterministic image preprocessing.

All operations are safe, reversible-in-intent transforms that do not add
clinical information. Augmentation (which does add variation) lives in the
sibling ``augmentation`` package and is applied only to training data.
"""

from __future__ import annotations

from .artifact_removal import mask_background, suppress_highlights
from .color_correction import apply_channel_gains, gray_world, standardize_channels
from .crop_retina import center_crop, crop_retina, find_retina_bbox
from .illumination_correction import correct_illumination, estimate_background
from .normalize import Normalize, normalize, to_float
from .pipeline import PipelineError, PreprocessingPipeline, resolve_step
from .resize import letterbox, resize_image

__all__ = [
    "mask_background",
    "suppress_highlights",
    "apply_channel_gains",
    "gray_world",
    "standardize_channels",
    "center_crop",
    "crop_retina",
    "find_retina_bbox",
    "correct_illumination",
    "estimate_background",
    "Normalize",
    "normalize",
    "to_float",
    "PipelineError",
    "PreprocessingPipeline",
    "resolve_step",
    "letterbox",
    "resize_image",
]
