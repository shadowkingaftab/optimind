"""Vision Transformer backbones (torchvision).

Wraps ``torchvision.models.vit_*`` and returns a spatial feature map by
reshaping patch tokens, so Grad-CAM-style methods can consume the output.
Pretrained weights are never downloaded; supply ``weights_path`` or keep
``pretrained`` off.
"""

from __future__ import annotations

from typing import Optional

from eyedx_ml.errors import ArtifactUnavailableError, DependencyError

__all__ = ["VIT_VARIANTS", "build_vision_transformer"]

VIT_VARIANTS = {
    "vit_b_16": 768,
    "vit_b_32": 768,
    "vit_l_16": 1024,
    "vit_l_32": 1024,
}


def _torch():
    try:
        import torch
        import torchvision
    except Exception as exc:  # pragma: no cover - optional dependency
        raise DependencyError(
            "torch and torchvision are required for ViT backbones "
            "(install: pip install torch torchvision)"
        ) from exc
    return torch, torchvision


def build_vision_transformer(
    name: str = "vit_b_16",
    *,
    pretrained: bool = False,
    weights_path: Optional[str] = None,
    in_channels: int = 3,
):
    if name not in VIT_VARIANTS:
        raise ValueError(f"unknown vit variant: {name}")
    if pretrained and not weights_path:
        raise ArtifactUnavailableError(
            "pretrained vit requested but no weights_path supplied "
            "(INPUT_REQUIRED: licensed weights)"
        )
    torch, torchvision = _torch()
    constructor = getattr(torchvision.models, name)

    class _FeatureViT(torch.nn.Module):
        def __init__(self) -> None:
            super().__init__()
            base = constructor(weights=None)
            self.conv_proj = base.conv_proj
            self.class_token = base.class_token
            self.encoder = base.encoder
            self.seq_length = None
            self.out_channels = VIT_VARIANTS[name]
            self.patch_size = getattr(base, "patch_size", 16)

        def forward(self, x):
            n = x.shape[0]
            x = self.conv_proj(x)  # (B, C, gh, gw)
            gh, gw = x.shape[-2], x.shape[-1]
            x = x.flatten(2).transpose(1, 2)  # (B, N, C)
            x = torch.cat([self.class_token.expand(n, -1, -1), x], dim=1)
            x = self.encoder(x)
            tokens = x[:, 1:, :]  # drop class token
            return tokens.transpose(1, 2).reshape(n, self.out_channels, gh, gw)

    module = _FeatureViT()
    if in_channels != 3:
        module.conv_proj = torch.nn.Conv2d(
            in_channels,
            module.out_channels,
            kernel_size=module.patch_size,
            stride=module.patch_size,
        )
    if weights_path:
        try:
            state = torch.load(weights_path, map_location="cpu")
        except Exception as exc:  # pragma: no cover - depends on artifact
            raise ArtifactUnavailableError(
                "could not load pretrained weights for vit"
            ) from exc
        if isinstance(state, dict) and "state_dict" in state:
            state = state["state_dict"]
        module.load_state_dict(state, strict=False)
    return module
