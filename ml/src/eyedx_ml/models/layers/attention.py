"""Attention layers."""

from __future__ import annotations

from typing import Optional

from eyedx_ml.errors import DependencyError

__all__ = ["channel_attention", "spatial_attention"]


def _torch():
    try:
        import torch
    except Exception as exc:  # pragma: no cover - optional dependency
        raise DependencyError("torch is required for attention layers") from exc
    return torch


def channel_attention(channels: int, reduction: int = 16):
    """Squeeze-and-excitation channel attention module."""
    torch = _torch()
    hidden = max(1, channels // reduction)

    class _ChannelAttention(torch.nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.avg_pool = torch.nn.AdaptiveAvgPool2d(1)
            self.max_pool = torch.nn.AdaptiveMaxPool2d(1)
            self.mlp = torch.nn.Sequential(
                torch.nn.Conv2d(channels, hidden, 1, bias=False),
                torch.nn.ReLU(inplace=True),
                torch.nn.Conv2d(hidden, channels, 1, bias=False),
            )
            self.sigmoid = torch.nn.Sigmoid()

        def forward(self, x):
            avg = self.mlp(self.avg_pool(x))
            mx = self.mlp(self.max_pool(x))
            return x * self.sigmoid(avg + mx)

    return _ChannelAttention()


def spatial_attention(kernel_size: int = 7):
    """Spatial attention over channel-wise avg/max maps."""
    torch = _torch()

    class _SpatialAttention(torch.nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.conv = torch.nn.Conv2d(
                2, 1, kernel_size=kernel_size, padding=kernel_size // 2, bias=False
            )
            self.sigmoid = torch.nn.Sigmoid()

        def forward(self, x):
            avg = x.mean(dim=1, keepdim=True)
            mx = x.max(dim=1, keepdim=True).values
            return x * self.sigmoid(self.conv(torch.cat([avg, mx], dim=1)))

    return _SpatialAttention()
