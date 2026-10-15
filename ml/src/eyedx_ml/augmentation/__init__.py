"""Training-time augmentation.

Augmentations add variation to the training split only and must never be applied
to validation, test or external-test data. Every operation is seeded for
reproducibility.
"""

from __future__ import annotations

from .augmentation_factory import AugmentationError, build_augmentation, build_mixer
from .cutmix import cutmix_batch, rand_bbox
from .geometric import (
    apply_geometric,
    horizontal_flip,
    random_crop,
    random_rotate,
    rotate90,
    vertical_flip,
)
from .mixup import mixup_batch, sample_lambda
from .noise import apply_noise, gaussian_blur, gaussian_noise, salt_pepper
from .photometric import (
    adjust_brightness,
    adjust_contrast,
    adjust_gamma,
    apply_photometric,
    channel_jitter,
)

__all__ = [
    "AugmentationError",
    "build_augmentation",
    "build_mixer",
    "cutmix_batch",
    "rand_bbox",
    "apply_geometric",
    "horizontal_flip",
    "random_crop",
    "random_rotate",
    "rotate90",
    "vertical_flip",
    "mixup_batch",
    "sample_lambda",
    "apply_noise",
    "gaussian_blur",
    "gaussian_noise",
    "salt_pepper",
    "adjust_brightness",
    "adjust_contrast",
    "adjust_gamma",
    "apply_photometric",
    "channel_jitter",
]
