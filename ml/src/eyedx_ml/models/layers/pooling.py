"""Pooling layers."""

from __future__ import annotations

from eyedx_ml.errors import DependencyError

__all__ = ["global_pool", "concat_pool"]


def _torch():
    try:
        import torch
    except Exception as exc:  # pragma: no cover - optional dependency
        raise DependencyError("torch is required for pooling layers") from exc
    return torch


def global_pool(mode: str = "avg"):
    """Return a module pooling (B, C, H, W) to (B, C)."""
    torch = _torch()
    if mode == "avg":
        return torch.nn.AdaptiveAvgPool2d(1)
    if mode == "max":
        return torch.nn.AdaptiveMaxPool2d(1)
    raise ValueError(f"unknown pooling mode: {mode}")


def concat_pool():
    """Average+max concatenated pooling: (B, C, H, W) -> (B, 2C)."""
    torch = _torch()

    class _ConcatPool(torch.nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.avg = torch.nn.AdaptiveAvgPool2d(1)
            self.max = torch.nn.AdaptiveMaxPool2d(1)

        def forward(self, x):
            avg = self.avg(x).flatten(1)
            mx = self.max(x).flatten(1)
            return torch.cat([avg, mx], dim=1)

    return _ConcatPool()
