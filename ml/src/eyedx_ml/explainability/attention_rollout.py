"""Attention rollout for transformer models."""

from __future__ import annotations

from typing import Optional

import numpy as np

from eyedx_ml.errors import DependencyError, NotConfiguredError

__all__ = ["attention_rollout"]


def _torch():
    try:
        import torch
    except Exception as exc:  # pragma: no cover - optional dependency
        raise DependencyError("torch is required for attention rollout") from exc
    return torch


def attention_rollout(
    attention_maps,
    *,
    discard_ratio: float = 0.9,
    grid_size: Optional[tuple] = None,
) -> np.ndarray:
    """Aggregate multi-head attention into a spatial rollout map.

    ``attention_maps`` is a sequence of per-layer attention tensors of shape
    (B, heads, tokens, tokens). The class token row is used and reshaped to
    ``grid_size`` (gh, gw). Attention must be captured via hooks by the caller.
    """
    torch = _torch()
    if not attention_maps:
        raise NotConfiguredError("no attention maps supplied")
    result = None
    for attn in attention_maps:
        attn = attn.detach()
        if attn.dim() != 4:
            raise NotConfiguredError("expected attention of shape (B, heads, N, N)")
        a = attn.mean(dim=1)[0]  # (N, N)
        if discard_ratio > 0:
            flat = a.flatten()
            k = int(flat.numel() * discard_ratio)
            if k > 0:
                threshold = torch.topk(flat, k, largest=False).values[-1]
                a = torch.where(a <= threshold, torch.zeros_like(a), a)
        a = a + torch.eye(a.shape[0], device=a.device)
        a = a / a.sum(dim=-1, keepdim=True)
        result = a if result is None else torch.matmul(a, result)

    mask = result[0, 1:]  # drop class token
    n = mask.numel()
    if grid_size is not None:
        gh, gw = grid_size
    else:
        side = int(round(n ** 0.5))
        gh = gw = side
    if gh * gw != n:
        gh, gw = n, 1
    heatmap = mask.reshape(gh, gw).detach().cpu().numpy()
    if heatmap.max() > 0:
        heatmap = heatmap / heatmap.max()
    return heatmap
