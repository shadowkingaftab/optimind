"""Explanation validation and sanity checks."""

from __future__ import annotations

from typing import Any, Dict, Optional

import numpy as np

__all__ = ["validate_heatmap", "deletion_score", "insertion_score"]


def validate_heatmap(
    heatmap: np.ndarray, *, expected_shape: Optional[tuple] = None
) -> Dict[str, Any]:
    """Check a heatmap is finite, in [0, 1] and the expected shape."""
    heatmap = np.asarray(heatmap, dtype=float)
    result: Dict[str, Any] = {
        "shape": tuple(heatmap.shape),
        "finite": bool(np.isfinite(heatmap).all()),
        "min": float(np.nanmin(heatmap)) if heatmap.size else None,
        "max": float(np.nanmax(heatmap)) if heatmap.size else None,
        "in_unit_range": bool(
            heatmap.size and heatmap.min() >= -1e-6 and heatmap.max() <= 1 + 1e-6
        ),
    }
    if expected_shape is not None:
        result["shape_matches"] = tuple(heatmap.shape) == tuple(expected_shape)
    return result


def _ranked_pixels(heatmap: np.ndarray):
    order = np.argsort(-np.asarray(heatmap, dtype=float).ravel())
    return order


def deletion_score(heatmap: np.ndarray, curve_scores) -> float:
    """Area under the deletion curve. Higher means the model relies on the
    highlighted regions (better). ``curve_scores`` are probabilities from the
    caller after progressive deletion.
    """
    values = np.asarray(curve_scores, dtype=float)
    if values.size == 0:
        return float("nan")
    return float(values.mean())


def insertion_score(heatmap: np.ndarray, curve_scores) -> float:
    values = np.asarray(curve_scores, dtype=float)
    if values.size == 0:
        return float("nan")
    return float(values.mean())
