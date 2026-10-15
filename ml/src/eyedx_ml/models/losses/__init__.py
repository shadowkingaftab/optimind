"""Loss functions."""

from __future__ import annotations

from .dice_loss import dice_loss, soft_dice
from .focal_loss import FocalLoss, focal_loss
from .multitask_loss import MultiTaskLoss, combine
from .weighted_bce import weighted_bce

__all__ = [
    "FocalLoss",
    "focal_loss",
    "weighted_bce",
    "soft_dice",
    "dice_loss",
    "MultiTaskLoss",
    "combine",
]
