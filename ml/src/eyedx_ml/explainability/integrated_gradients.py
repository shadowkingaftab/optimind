"""Integrated gradients (captum preferred, manual fallback)."""

from __future__ import annotations

from typing import Optional

import numpy as np

from eyedx_ml.errors import DependencyError, NotConfiguredError

__all__ = ["integrated_gradients"]


def _torch():
    try:
        import torch
    except Exception as exc:  # pragma: no cover - optional dependency
        raise DependencyError("torch is required for integrated gradients") from exc
    return torch


def integrated_gradients(
    model,
    input_tensor,
    *,
    target: Optional[int] = None,
    baseline=None,
    steps: int = 32,
) -> np.ndarray:
    """Return an attribution map (H, W) summarising gradient x input.

    Uses captum when available, otherwise a Riemann-sum approximation. The map is
    reduced to a 2D heatmap by averaging over channels and taking the absolute
    value.
    """
    torch = _torch()
    model.eval()
    if baseline is None:
        baseline = torch.zeros_like(input_tensor)

    try:
        from captum.attr import IntegratedGradients

        wrapper = model
        ig = IntegratedGradients(wrapper)
        attributions = ig.attribute(
            input_tensor, baselines=baseline, target=target, n_steps=steps
        )
    except Exception:
        attributions = _manual_ig(model, input_tensor, baseline, target, steps)

    attr = attributions[0].detach().cpu().numpy()
    if attr.ndim == 3:
        attr = np.abs(attr).mean(axis=0)
    if attr.max() > 0:
        attr = attr / attr.max()
    return attr


def _manual_ig(model, input_tensor, baseline, target, steps: int):
    torch = _torch()
    alphas = torch.linspace(0, 1, steps, device=input_tensor.device).view(-1, 1, 1, 1)
    diff = (input_tensor - baseline)
    total_grad = torch.zeros_like(input_tensor)
    for alpha in alphas:
        scaled = (baseline + alpha * diff).clone().requires_grad_(True)
        output = model(scaled)
        if isinstance(output, dict):
            raise NotConfiguredError("integrated gradients needs a single-output model")
        if target is None:
            target = int(output.argmax(dim=-1).item())
        score = output[0, target]
        grad = torch.autograd.grad(score, scaled)[0]
        total_grad += grad
    return diff * (total_grad / steps)
