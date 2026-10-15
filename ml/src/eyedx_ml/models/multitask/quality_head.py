"""Image-quality head for multi-task models."""

from __future__ import annotations

from typing import Optional

from eyedx_ml.errors import DependencyError, NotConfiguredError

__all__ = ["build_quality_head"]


def _torch():
    try:
        import torch
    except Exception as exc:  # pragma: no cover - optional dependency
        raise DependencyError("torch is required for multi-task heads") from exc
    return torch


def build_quality_head(
    in_features: int,
    *,
    num_outputs: int = 1,
    regression: bool = False,
    hidden_dim: Optional[int] = None,
    dropout: float = 0.0,
):
    """Return a quality head.

    ``regression=True`` yields a scalar quality score (B, num_outputs=1);
    otherwise it yields classification logits over ``num_outputs`` quality
    grades. Quality grade definitions are INPUT_REQUIRED.
    """
    torch = _torch()
    from eyedx_ml.models.layers import classification_head

    if regression:
        if num_outputs != 1:
            raise NotConfiguredError("quality regression supports a single output")
        return classification_head(
            in_features, 1, hidden_dim=hidden_dim, dropout=dropout, activation="none"
        )
    if not num_outputs or num_outputs < 2:
        raise NotConfiguredError(
            "quality classification needs >= 2 grades (INPUT_REQUIRED)"
        )
    return classification_head(
        in_features,
        num_outputs,
        hidden_dim=hidden_dim,
        dropout=dropout,
        activation="none",
    )
