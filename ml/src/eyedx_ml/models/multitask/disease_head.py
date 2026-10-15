"""Disease classification head for multi-task models."""

from __future__ import annotations

from typing import Optional

from eyedx_ml.errors import DependencyError, NotConfiguredError

__all__ = ["build_disease_head"]


def _torch():
    try:
        import torch
    except Exception as exc:  # pragma: no cover - optional dependency
        raise DependencyError("torch is required for multi-task heads") from exc
    return torch


def build_disease_head(
    in_features: int,
    num_labels: int,
    *,
    hidden_dim: Optional[int] = None,
    dropout: float = 0.0,
):
    """Return a disease head producing (B, num_labels) logits."""
    from eyedx_ml.models.layers import classification_head

    if not num_labels or num_labels < 1:
        raise NotConfiguredError(
            "disease head requires num_labels from the approved label map"
        )
    return classification_head(
        in_features, num_labels, hidden_dim=hidden_dim, dropout=dropout, activation="none"
    )
