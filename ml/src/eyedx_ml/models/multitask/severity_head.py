"""Ordinal severity head for multi-task models."""

from __future__ import annotations

from typing import Optional

from eyedx_ml.errors import DependencyError, NotConfiguredError

__all__ = ["build_severity_head", "expected_severity"]


def _torch():
    try:
        import torch
    except Exception as exc:  # pragma: no cover - optional dependency
        raise DependencyError("torch is required for multi-task heads") from exc
    return torch


def build_severity_head(
    in_features: int,
    num_levels: int,
    *,
    hidden_dim: Optional[int] = None,
    dropout: float = 0.0,
):
    """Return an ordinal severity head producing (B, num_levels) logits.

    Grade ordering/definitions are INPUT_REQUIRED; only the ordering mechanism is
    implemented here.
    """
    from eyedx_ml.models.layers import classification_head

    if not num_levels or num_levels < 2:
        raise NotConfiguredError(
            "severity head requires >= 2 ordered levels (INPUT_REQUIRED)"
        )
    return classification_head(
        in_features,
        num_levels,
        hidden_dim=hidden_dim,
        dropout=dropout,
        activation="none",
    )


def expected_severity(logits, *, num_levels: Optional[int] = None):
    """Expected ordinal level from logits (softmax over ordered levels)."""
    torch = _torch()
    probs = torch.softmax(logits, dim=-1)
    levels = num_levels or int(logits.shape[-1])
    weights = torch.arange(levels, device=logits.device, dtype=probs.dtype)
    return (probs * weights).sum(dim=-1)
