"""A minimal U-Net for retinal segmentation tasks."""

from __future__ import annotations

from typing import List

from eyedx_ml.errors import DependencyError, NotConfiguredError

__all__ = ["build_unet"]


def _torch():
    try:
        import torch
    except Exception as exc:  # pragma: no cover - optional dependency
        raise DependencyError("torch is required to build U-Net") from exc
    return torch


def build_unet(
    in_channels: int = 3,
    num_classes: int = 2,
    *,
    base_channels: int = 64,
    depth: int = 4,
):
    """Return a U-Net module producing per-pixel logits (B, num_classes, H, W)."""
    torch = _torch()
    if num_classes < 2:
        raise NotConfiguredError("segmentation needs >= 2 classes (background + 1)")

    class _DoubleConv(torch.nn.Module):
        def __init__(self, cin: int, cout: int) -> None:
            super().__init__()
            self.block = torch.nn.Sequential(
                torch.nn.Conv2d(cin, cout, 3, padding=1, bias=False),
                torch.nn.BatchNorm2d(cout),
                torch.nn.ReLU(inplace=True),
                torch.nn.Conv2d(cout, cout, 3, padding=1, bias=False),
                torch.nn.BatchNorm2d(cout),
                torch.nn.ReLU(inplace=True),
            )

        def forward(self, x):
            return self.block(x)

    class _UNet(torch.nn.Module):
        def __init__(self) -> None:
            super().__init__()
            chans: List[int] = [base_channels * (2 ** i) for i in range(depth + 1)]
            self.downs = torch.nn.ModuleList()
            self.pool = torch.nn.MaxPool2d(2)
            prev = in_channels
            for c in chans[:-1]:
                self.downs.append(_DoubleConv(prev, c))
                prev = c
            self.bottleneck = _DoubleConv(prev, chans[-1])
            self.ups = torch.nn.ModuleList()
            self.upconvs = torch.nn.ModuleList()
            for c in reversed(chans[:-1]):
                self.upconvs.append(torch.nn.ConvTranspose2d(c * 2, c, 2, stride=2))
                self.ups.append(_DoubleConv(c * 2, c))
            self.head = torch.nn.Conv2d(chans[0], num_classes, 1)

        def forward(self, x):
            skips = []
            for down in self.downs:
                x = down(x)
                skips.append(x)
                x = self.pool(x)
            x = self.bottleneck(x)
            for upconv, up, skip in zip(self.upconvs, self.ups, reversed(skips)):
                x = upconv(x)
                x = torch.cat([skip, x], dim=1)
                x = up(x)
            return self.head(x)

    return _UNet()
