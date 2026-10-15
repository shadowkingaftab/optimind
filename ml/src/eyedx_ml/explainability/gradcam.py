"""Grad-CAM explanations.

Hook-based Grad-CAM that works with any module exposing a spatial feature map.
Explanations are for review/quality purposes and are never shown as diagnostic
evidence.
"""

from __future__ import annotations

from typing import Optional

import numpy as np

from eyedx_ml.errors import DependencyError, NotConfiguredError

__all__ = ["GradCAM"]


def _torch():
    try:
        import torch
    except Exception as exc:  # pragma: no cover - optional dependency
        raise DependencyError("torch is required for Grad-CAM") from exc
    return torch


class GradCAM:
    """Compute Grad-CAM maps for a target layer.

    ``target_layer`` should be the backbone's last spatial stage. ``generate``
    returns a normalised 2D heatmap for the selected output channel.
    """

    def __init__(self, model, target_layer) -> None:
        if model is None or target_layer is None:
            raise NotConfiguredError("GradCAM requires a model and target_layer")
        self.model = model
        self.target_layer = target_layer
        self._activations = None
        self._gradients = None
        self._handles = []

    def _register(self) -> None:
        def forward_hook(_module, _inp, output):
            self._activations = output.detach()

        def backward_hook(_module, _grad_in, grad_out):
            self._gradients = grad_out[0].detach()

        self._handles.append(self.target_layer.register_forward_hook(forward_hook))
        self._handles.append(
            self.target_layer.register_full_backward_hook(backward_hook)
        )

    def _remove(self) -> None:
        for handle in self._handles:
            handle.remove()
        self._handles = []

    def generate(self, input_tensor, *, target: Optional[int] = None):
        torch = _torch()
        self.model.eval()
        self._register()
        try:
            output = self.model(input_tensor)
            if isinstance(output, dict):
                raise NotConfiguredError(
                    "GradCAM target a specific head; pass a single-output model"
                )
            if target is None:
                target = int(output.argmax(dim=-1).item())
            self.model.zero_grad()
            score = output[0, target]
            score.backward(retain_graph=False)
            if self._gradients is None or self._activations is None:
                raise NotConfiguredError("hooks captured no activations")
            weights = self._gradients.mean(dim=(2, 3), keepdim=True)
            cam = (weights * self._activations).sum(dim=1, keepdim=True)
            cam = torch.relu(cam)
            cam = torch.nn.functional.interpolate(
                cam, size=input_tensor.shape[-2:], mode="bilinear", align_corners=False
            )
            cam = cam[0, 0].detach().cpu().numpy()
            if cam.max() > 0:
                cam = cam / cam.max()
            return cam
        finally:
            self._remove()
