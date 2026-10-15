"""ConvNeXt backbones (torchvision).

Returns the ``features`` feature map. Pretrained weights are never downloaded;
supply an explicit ``weights_path`` or keep ``pretrained`` off.
"""

from __future__ import annotations

from typing import Optional

from eyedx_ml.errors import ArtifactUnavailableError, DependencyError

__all__ = ["CONVNEXT_VARIANTS", "build_convnext"]

CONVNEXT_VARIANTS = (
    "convnext_tiny",
    "convnext_small",
    "convnext_base",
    "convnext_large",
)


def _torch():
    try:
        import torch
        import torchvision
    except Exception as exc:  # pragma: no cover - optional dependency
        raise DependencyError(
            "torch and torchvision are required for ConvNeXt backbones "
            "(install: pip install torch torchvision)"
        ) from exc
    return torch, torchvision


def build_convnext(
    name: str = "convnext_tiny",
    *,
    pretrained: bool = False,
    weights_path: Optional[str] = None,
    in_channels: int = 3,
):
    if name not in CONVNEXT_VARIANTS:
        raise ValueError(f"unknown convnext variant: {name}")
    if pretrained and not weights_path:
        raise ArtifactUnavailableError(
            "pretrained convnext requested but no weights_path supplied "
            "(INPUT_REQUIRED: licensed weights)"
        )
    torch, torchvision = _torch()
    constructor = getattr(torchvision.models, name)

    class _FeatureConvNeXt(torch.nn.Module):
        def __init__(self) -> None:
            super().__init__()
            base = constructor(weights=None)
            self.features = base.features
            self.out_channels = base.classifier[2].in_features

        def forward(self, x):
            return self.features(x)

    module = _FeatureConvNeXt()
    if in_channels != 3:
        first = module.features[0]
        conv = first[0]
        module.features[0][0] = torch.nn.Conv2d(
            in_channels,
            conv.out_channels,
            kernel_size=conv.kernel_size,
            stride=conv.stride,
            padding=conv.padding,
            bias=conv.bias is not None,
        )
    if weights_path:
        try:
            state = torch.load(weights_path, map_location="cpu")
        except Exception as exc:  # pragma: no cover - depends on artifact
            raise ArtifactUnavailableError(
                "could not load pretrained weights for convnext"
            ) from exc
        if isinstance(state, dict) and "state_dict" in state:
            state = state["state_dict"]
        module.load_state_dict(state, strict=False)
    return module
