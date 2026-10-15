"""Operating-point / threshold selection.

Thresholds are derived from validation data under a stated criterion. They are
never invented. Any chosen threshold must be reviewed and approved before it is
used for screening decisions.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

import numpy as np

from eyedx_ml.metrics.sensitivity import sensitivity_at_threshold
from eyedx_ml.metrics.specificity import specificity_at_threshold

__all__ = ["youden_threshold", "threshold_for_sensitivity", "threshold_for_specificity", "optimize_threshold"]


def _grid(y_score: np.ndarray, n: int = 200) -> np.ndarray:
    lo, hi = float(np.min(y_score)), float(np.max(y_score))
    if hi <= lo:
        hi = lo + 1e-6
    return np.linspace(lo, hi, n)


def youden_threshold(y_true: np.ndarray, y_score: np.ndarray, *, n: int = 200) -> Dict[str, Any]:
    """Threshold maximising Youden's J = sensitivity + specificity - 1."""
    best: Dict[str, Any] = {"threshold": None, "youden_j": None}
    for t in _grid(np.asarray(y_score, dtype=float), n):
        sens = sensitivity_at_threshold(y_true, y_score, t)
        spec = specificity_at_threshold(y_true, y_score, t)
        if sens is None or spec is None:
            continue
        j = sens + spec - 1
        if best["youden_j"] is None or j > best["youden_j"]:
            best = {"threshold": float(t), "youden_j": float(j), "sensitivity": sens, "specificity": spec}
    return best


def threshold_for_sensitivity(
    y_true: np.ndarray, y_score: np.ndarray, target: float, *, n: int = 200
) -> Dict[str, Any]:
    """Lowest threshold achieving at least ``target`` sensitivity."""
    y_score = np.asarray(y_score, dtype=float)
    candidates = []
    for t in sorted(_grid(y_score, n), reverse=True):
        sens = sensitivity_at_threshold(y_true, y_score, t)
        if sens is not None and sens >= target:
            candidates.append((t, sens))
    if not candidates:
        return {"threshold": None, "target_sensitivity": target, "achieved": None}
    t, sens = candidates[-1]
    return {
        "threshold": float(t),
        "target_sensitivity": target,
        "achieved": sens,
        "specificity": specificity_at_threshold(y_true, y_score, t),
    }


def threshold_for_specificity(
    y_true: np.ndarray, y_score: np.ndarray, target: float, *, n: int = 200
) -> Dict[str, Any]:
    """Highest threshold achieving at least ``target`` specificity."""
    y_score = np.asarray(y_score, dtype=float)
    candidates = []
    for t in _grid(y_score, n):
        spec = specificity_at_threshold(y_true, y_score, t)
        if spec is not None and spec >= target:
            candidates.append((t, spec))
    if not candidates:
        return {"threshold": None, "target_specificity": target, "achieved": None}
    t, spec = candidates[-1]
    return {
        "threshold": float(t),
        "target_specificity": target,
        "achieved": spec,
        "sensitivity": sensitivity_at_threshold(y_true, y_score, t),
    }


def optimize_threshold(
    y_true: np.ndarray,
    y_score: np.ndarray,
    *,
    criterion: str = "youden",
    target: Optional[float] = None,
    fixed: Optional[float] = None,
) -> Dict[str, Any]:
    """Select an operating threshold under a named criterion."""
    if criterion == "fixed":
        if fixed is None:
            raise ValueError("fixed criterion requires a `fixed` threshold")
        return {"criterion": "fixed", "threshold": float(fixed)}
    if criterion == "youden":
        result = youden_threshold(y_true, y_score)
        result["criterion"] = "youden"
        return result
    if criterion == "target_sensitivity":
        if target is None:
            raise ValueError("target_sensitivity requires `target`")
        result = threshold_for_sensitivity(y_true, y_score, target)
        result["criterion"] = "target_sensitivity"
        return result
    if criterion == "target_specificity":
        if target is None:
            raise ValueError("target_specificity requires `target`")
        result = threshold_for_specificity(y_true, y_score, target)
        result["criterion"] = "target_specificity"
        return result
    raise ValueError(f"unknown threshold criterion: {criterion}")
