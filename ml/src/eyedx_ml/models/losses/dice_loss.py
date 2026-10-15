"""Dice and soft-Dice losses for segmentation."""

from __future__ import annotations

from eyedx_ml.errors import DependencyError

__all__ = ["soft_dice", "dice_loss"]


def _torch():
    try:
        import torch
        import torch.nn.functional as F
    except Exception as exc:  # pragma: no cover - optional dependency
        raise DependencyError("torch is required for losses") from exc
    return torch, F


def soft_dice(probs, targets, *, eps: float = 1e-6):
    """Mean soft Dice over the class dimension.

    ``probs`` is (B, C, ...) probabilities, ``targets`` one-hot/float of equal
    shape.
    """
    torch, _ = _torch()
    dims = tuple(range(2, probs.dim()))
    intersection = (probs * targets).sum(dim=dims)
    union = probs.sum(dim=dims) + targets.sum(dim=dims)
    dice = (2 * intersection + eps) / (union + eps)
    return 1.0 - dice.mean()


def dice_loss(logits, targets, *, eps: float = 1e-6):
    torch, F = _torch()
    probs = torch.softmax(logits, dim=1)
    if targets.dim() == logits.dim() - 1:
        targets = F.one_hot(targets.long(), num_classes=logits.shape[1])
        targets = targets.permute(0, -1, *range(1, targets.dim() - 1)).float()
    else:
        targets = targets.to(probs.dtype)
    return soft_dice(probs, targets, eps=eps)
