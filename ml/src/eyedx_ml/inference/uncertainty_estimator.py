"""Uncertainty estimation and abstention decisions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

import numpy as np

from eyedx_ml.errors import DependencyError, NotConfiguredError

__all__ = ["UncertaintyResult", "estimate_uncertainty", "entropy", "max_prob_uncertainty", "mc_dropout"]


@dataclass
class UncertaintyResult:
    method: str
    value: float
    is_uncertain: bool
    threshold: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "method": self.method,
            "value": float(self.value),
            "threshold": self.threshold,
            "is_uncertain": self.is_uncertain,
        }


def max_prob_uncertainty(probs: np.ndarray) -> float:
    probs = np.asarray(probs, dtype=float)
    return float(1.0 - probs.max())


def entropy(probs: np.ndarray) -> float:
    """Normalised Shannon entropy in [0, 1]."""
    probs = np.asarray(probs, dtype=float).ravel()
    probs = probs / max(probs.sum(), 1e-12)
    h = -float((probs * np.log(np.clip(probs, 1e-12, 1.0))).sum())
    denom = np.log(probs.size) if probs.size > 1 else 1.0
    return float(h / denom) if denom > 0 else 0.0


def mc_dropout(model, input_tensor, *, samples: int = 20) -> float:
    """Predictive variance via MC dropout (model must have dropout layers)."""
    try:
        import torch
    except Exception as exc:  # pragma: no cover - optional dependency
        raise DependencyError("torch is required for MC dropout") from exc
    model.train()  # keep dropout active
    outputs = []
    with torch.no_grad():
        for _ in range(int(samples)):
            out = model(input_tensor)
            if isinstance(out, dict):
                raise NotConfiguredError("MC dropout needs a single-output model")
            outputs.append(torch.sigmoid(out).cpu().numpy())
    stack = np.stack(outputs, axis=0)
    model.eval()
    return float(stack.var(axis=0).mean())


def estimate_uncertainty(
    probs: np.ndarray,
    *,
    method: str = "max_prob",
    threshold: Optional[float] = None,
    model=None,
    input_tensor=None,
    mc_samples: int = 20,
) -> UncertaintyResult:
    probs = np.asarray(probs, dtype=float)
    if method == "max_prob":
        value = max_prob_uncertainty(probs)
    elif method == "entropy":
        value = entropy(probs)
    elif method == "mc_dropout":
        if model is None or input_tensor is None:
            raise NotConfiguredError("mc_dropout requires a model and input tensor")
        value = mc_dropout(model, input_tensor, samples=mc_samples)
    else:
        raise NotConfiguredError(f"unknown uncertainty method: {method}")

    is_uncertain = threshold is not None and value >= float(threshold)
    return UncertaintyResult(
        method=method, value=value, is_uncertain=is_uncertain, threshold=threshold
    )
