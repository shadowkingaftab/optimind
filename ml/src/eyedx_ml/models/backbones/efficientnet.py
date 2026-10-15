"""EfficientNet backbones (torchvision).

Returns the ``features`` feature map. Pretrained weights are never downloaded;
supply an explicit ``weights_path`` or keep ``pretrained`` off.
"""

from __future__ import annotations

from typing import Optional

from eyedx_ml.errors import ArtifactUnavailableError, DependencyError

__all__ = ["EFFICIENTNET_VARIANTS", "build_efficientnet"]

EFFICIENTNET_VARIANTS = (
    "efficientnet_b0",
    "efficientnet_b1",
    "efficientnet_b2",
    "efficientnet_b3",
    "efficientnet_b4",
    "efficientnet_b5",
    "efficientnet_b6",
    "efficientnet_b7",
)


def _torch():
    try:
        import torch
        import torchvision
    except Exception as exc:  # pragma: no cover - optional dependency
        raise DependencyError(
            "torch and torchvision are required for EfficientNet backbones "
            "(install: pip install torch torchvision)"
        ) from exc
    return torch, torchvision


def build_efficientnet(
    name: str = "efficientnet_b0",
    *,
    pretrained: bool = False,
    weights_path: Optional[str] = None,
    in_channels: int = 3,
):
    if name not in EFFICIENTNET_VARIANTS:
        raise ValueError(f"unknown efficientnet variant: {name}")
    if pretrained and not weights_path:
        raise ArtifactUnavailableError(
            "pretrained efficientnet requested but no weights_path supplied "
            "(INPUT_REQUIRED: licensed weights)"
        )
    torch, torchvision = _torch()
    constructor = getattr(torchvision.models, name)

    class _FeatureEfficientNet(torch.nn.Module):
        def __init__(self) -> None:
            super().__init__()
            base = constructor(weights=None)
            self.features = base.features
            self.out_channels = base.classifier[1].in_features

        def forward(self, x):
            return self.features(x)

    module = _FeatureEfficientNet()
    if in_channels != 3:
        first = module.features[0]
        conv = first[0] if isinstance(first, torch.nn.Sequential) else first
        out_ch = conv.out_channels
        kernel = conv.kernel_size
        stride = conv.stride
        padding = conv.padding
        new_conv = torch.nn.Conv2d(
            in_channels, out_ch, kernel_size=kernel, stride=stride, padding=padding, bias=False
        )
        if isinstance(first, torch.nn.Sequential):
            first[0] = new_conv
        else:
            module.features[0] = new_conv
    if weights_path:
        try:
            state = torch.load(weights_path, map_location="cpu")
        except Exception as exc:  # pragma: no cover - depends on artifact
            raise ArtifactUnavailableError(
                "could not load pretrained weights for efficientnet"
            ) from exc
        if isinstance(state, dict) and "state_dict" in state:
            state = state["state_dict"]
        module.load_state_dict(state, strict=False)
    return module
