"""Classification heads."""

from __future__ import annotations

from typing import Optional

from eyedx_ml.errors import DependencyError

__all__ = ["classification_head"]


def _torch():
    try:
        import torch
    except Exception as exc:  # pragma: no cover - optional dependency
        raise DependencyError("torch is required for classification heads") from exc
    return torch


def classification_head(
    in_features: int,
    num_outputs: int,
    *,
    hidden_dim: Optional[int] = None,
    dropout: float = 0.0,
    activation: str = "none",
):
    """Return a head mapping pooled features (B, in_features) to logits.

    ``activation`` is applied to the output: ``none`` (logits, for loss),
    ``sigmoid`` (multi-label), or ``softmax`` (single-label/multiclass).
    """
    torch = _torch()
    layers = []
    last = in_features
    if hidden_dim:
        layers += [torch.nn.Linear(in_features, hidden_dim), torch.nn.ReLU(inplace=True)]
        last = hidden_dim
    if dropout and dropout > 0:
        layers.append(torch.nn.Dropout(p=float(dropout)))
    layers.append(torch.nn.Linear(last, num_outputs))

    if activation == "sigmoid":
        layers.append(torch.nn.Sigmoid())
    elif activation == "softmax":
        layers.append(torch.nn.Softmax(dim=-1))
    elif activation != "none":
        raise ValueError(f"unknown head activation: {activation}")

    return torch.nn.Sequential(*layers)
