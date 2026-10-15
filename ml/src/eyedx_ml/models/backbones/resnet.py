"""ResNet backbones (torchvision).

Builds a ResNet feature extractor returning the layer4 feature map so
explainability (Grad-CAM) can use spatial activations. Pretrained weights are
never downloaded: pass an explicit ``weights_path`` (supplied under licence) or
keep ``pretrained`` off.
"""

from __future__ import annotations

from typing import Optional

from eyedx_ml.errors import ArtifactUnavailableError, DependencyError

__all__ = ["RESNET_VARIANTS", "build_resnet"]

RESNET_VARIANTS = {
    "resnet18": 512,
    "resnet34": 512,
    "resnet50": 2048,
    "resnet101": 2048,
    "resnet152": 2048,
}


def _torch():
    try:
        import torch
        import torchvision
    except Exception as exc:  # pragma: no cover - optional dependency
        raise DependencyError(
            "torch and torchvision are required for ResNet backbones "
            "(install: pip install torch torchvision)"
        ) from exc
    return torch, torchvision


def _load_weights(module, weights_path: Optional[str]) -> None:
    if not weights_path:
        return
    torch, _ = _torch()
    try:
        state = torch.load(weights_path, map_location="cpu")
    except Exception as exc:  # pragma: no cover - depends on artifact
        raise ArtifactUnavailableError(
            "could not load pretrained weights for resnet"
        ) from exc
    if isinstance(state, dict) and "state_dict" in state:
        state = state["state_dict"]
    module.load_state_dict(state, strict=False)


def build_resnet(
    name: str = "resnet50",
    *,
    pretrained: bool = False,
    weights_path: Optional[str] = None,
    in_channels: int = 3,
):
    """Return a ResNet nn.Module whose forward yields a feature map."""
    if name not in RESNET_VARIANTS:
        raise ValueError(f"unknown resnet variant: {name}")
    if pretrained and not weights_path:
        raise ArtifactUnavailableError(
            "pretrained resnet requested but no weights_path supplied "
            "(INPUT_REQUIRED: licensed ImageNet/medical weights)"
        )
    torch, torchvision = _torch()
    constructors = {
        "resnet18": torchvision.models.resnet18,
        "resnet34": torchvision.models.resnet34,
        "resnet50": torchvision.models.resnet50,
        "resnet101": torchvision.models.resnet101,
        "resnet152": torchvision.models.resnet152,
    }

    class _FeatureResNet(torch.nn.Module):
        def __init__(self) -> None:
            super().__init__()
            base = constructors[name](weights=None)
            self.out_channels = RESNET_VARIANTS[name]
            self.stem = torch.nn.Sequential(
                base.conv1, base.bn1, base.relu, base.maxpool
            )
            self.layer1 = base.layer1
            self.layer2 = base.layer2
            self.layer3 = base.layer3
            self.layer4 = base.layer4

        def forward(self, x):
            x = self.stem(x)
            x = self.layer1(x)
            x = self.layer2(x)
            x = self.layer3(x)
            return self.layer4(x)

    module = _FeatureResNet()
    if in_channels != 3:
        module.stem[0] = torch.nn.Conv2d(
            in_channels, 64, kernel_size=7, stride=2, padding=3, bias=False
        )
    _load_weights(module, weights_path)
    return module
