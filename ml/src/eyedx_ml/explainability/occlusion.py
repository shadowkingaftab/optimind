"""Occlusion-sensitivity explanations."""

from __future__ import annotations

from typing import Optional

import numpy as np

from eyedx_ml.errors import DependencyError, NotConfiguredError

__all__ = ["occlusion_sensitivity"]


def _torch():
    try:
        import torch
    except Exception as exc:  # pragma: no cover - optional dependency
        raise DependencyError("torch is required for occlusion analysis") from exc
    return torch


def occlusion_sensitivity(
    model,
    input_tensor,
    *,
    target: Optional[int] = None,
    patch_size: int = 32,
    stride: Optional[int] = None,
    baseline_value: float = 0.0,
) -> np.ndarray:
    """Sliding-window occlusion: heatmap of score drop when a patch is masked."""
    torch = _torch()
    model.eval()
    stride = stride or patch_size
    _, _, height, width = input_tensor.shape

    with torch.no_grad():
        base_output = model(input_tensor)
        if isinstance(base_output, dict):
            raise NotConfiguredError("occlusion needs a single-output model")
        if target is None:
            target = int(base_output.argmax(dim=-1).item())
        base_score = float(base_output[0, target].item())

    heatmap = np.zeros((height, width), dtype=float)
    counts = np.zeros((height, width), dtype=float)
    for y in range(0, height, stride):
        for x in range(0, width, stride):
            y2 = min(y + patch_size, height)
            x2 = min(x + patch_size, width)
            occluded = input_tensor.clone()
            occluded[:, :, y:y2, x:x2] = baseline_value
            with torch.no_grad():
                out = model(occluded)
                score = float(out[0, target].item())
            heatmap[y:y2, x:x2] += (base_score - score)
            counts[y:y2, x:x2] += 1

    counts[counts == 0] = 1
    heatmap = heatmap / counts
    heatmap = np.clip(heatmap, 0, None)
    if heatmap.max() > 0:
        heatmap = heatmap / heatmap.max()
    return heatmap
