"""Focal loss."""

from __future__ import annotations

from typing import Optional

from eyedx_ml.errors import DependencyError

__all__ = ["focal_loss", "FocalLoss"]


def _torch():
    try:
        import torch
        import torch.nn.functional as F
    except Exception as exc:  # pragma: no cover - optional dependency
        raise DependencyError("torch is required for losses") from exc
    return torch, F


def focal_loss(
    logits,
    targets,
    *,
    gamma: float = 2.0,
    alpha: Optional[float] = None,
    reduction: str = "mean",
):
    """Binary focal loss on logits. ``targets`` are float in {0,1}, shape == logits."""
    torch, F = _torch()
    targets = targets.to(logits.dtype)
    bce = F.binary_cross_entropy_with_logits(logits, targets, reduction="none")
    p = torch.sigmoid(logits)
    p_t = p * targets + (1 - p) * (1 - targets)
    loss = bce * ((1 - p_t) ** gamma)
    if alpha is not None:
        alpha_t = alpha * targets + (1 - alpha) * (1 - targets)
        loss = alpha_t * loss
    if reduction == "mean":
        return loss.mean()
    if reduction == "sum":
        return loss.sum()
    return loss


class FocalLoss:
    def __new__(cls, *, gamma: float = 2.0, alpha: Optional[float] = None, reduction: str = "mean"):
        torch, _ = _torch()

        class _FocalLoss(torch.nn.Module):
            def __init__(self) -> None:
                super().__init__()
                self.gamma = gamma
                self.alpha = alpha
                self.reduction = reduction

            def forward(self, logits, targets):
                return focal_loss(
                    logits,
                    targets,
                    gamma=self.gamma,
                    alpha=self.alpha,
                    reduction=self.reduction,
                )

        return _FocalLoss()
