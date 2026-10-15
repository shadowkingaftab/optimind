"""Weighted binary cross-entropy loss."""

from __future__ import annotations

from typing import Optional, Sequence

from eyedx_ml.errors import DependencyError

__all__ = ["weighted_bce"]


def _torch():
    try:
        import torch
        import torch.nn.functional as F
    except Exception as exc:  # pragma: no cover - optional dependency
        raise DependencyError("torch is required for losses") from exc
    return torch, F


def weighted_bce(
    logits,
    targets,
    *,
    pos_weight: Optional[Sequence[float] | float] = None,
    reduction: str = "mean",
):
    """Binary cross-entropy with logits and optional positive weighting.

    ``pos_weight`` handles class imbalance; derive it from train-split
    statistics (never guess). Per-column values are supported for multi-label.
    """
    torch, F = _torch()
    pos_weight_t = None
    if pos_weight is not None:
        if isinstance(pos_weight, (int, float)):
            pos_weight = [float(pos_weight)]
        pos_weight_t = torch.as_tensor(pos_weight, dtype=logits.dtype, device=logits.device)
        if pos_weight_t.numel() == 1:
            pos_weight_t = pos_weight_t.item()
    return F.binary_cross_entropy_with_logits(
        logits, targets.to(logits.dtype), pos_weight=pos_weight_t, reduction=reduction
    )
