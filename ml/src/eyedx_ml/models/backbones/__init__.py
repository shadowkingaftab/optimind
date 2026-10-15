"""Backbone registry.

Backbones are built lazily (only importing torch/torchvision when actually
constructed). Every backbone returns a spatial feature map and exposes
``out_channels``.
"""

from __future__ import annotations

from typing import Callable, Dict

from eyedx_ml.errors import DependencyError

__all__ = ["BACKBONES", "create_backbone", "list_backbones"]


def _build_resnet(name, **kw):
    from .resnet import build_resnet

    return build_resnet(name, **kw)


def _build_efficientnet(name, **kw):
    from .efficientnet import build_efficientnet

    return build_efficientnet(name, **kw)


def _build_convnext(name, **kw):
    from .convnext import build_convnext

    return build_convnext(name, **kw)


def _build_vit(name, **kw):
    from .vision_transformer import build_vision_transformer

    return build_vision_transformer(name, **kw)


BACKBONES: Dict[str, Callable[..., object]] = {
    "resnet18": _build_resnet,
    "resnet34": _build_resnet,
    "resnet50": _build_resnet,
    "resnet101": _build_resnet,
    "resnet152": _build_resnet,
    "efficientnet_b0": _build_efficientnet,
    "efficientnet_b1": _build_efficientnet,
    "efficientnet_b2": _build_efficientnet,
    "efficientnet_b3": _build_efficientnet,
    "efficientnet_b4": _build_efficientnet,
    "efficientnet_b5": _build_efficientnet,
    "efficientnet_b6": _build_efficientnet,
    "efficientnet_b7": _build_efficientnet,
    "convnext_tiny": _build_convnext,
    "convnext_small": _build_convnext,
    "convnext_base": _build_convnext,
    "convnext_large": _build_convnext,
    "vit_b_16": _build_vit,
    "vit_b_32": _build_vit,
    "vit_l_16": _build_vit,
    "vit_l_32": _build_vit,
}


def list_backbones() -> list:
    return sorted(BACKBONES)


def create_backbone(
    name: str,
    *,
    pretrained: bool = False,
    weights_path: str | None = None,
    in_channels: int = 3,
):
    """Instantiate a backbone by name, returning a feature-extractor module."""
    builder = BACKBONES.get(name)
    if builder is None:
        raise DependencyError(
            f"unknown backbone {name!r}; available: {', '.join(list_backbones())}"
        )
    return builder(
        name,
        pretrained=pretrained,
        weights_path=weights_path,
        in_channels=in_channels,
    )
