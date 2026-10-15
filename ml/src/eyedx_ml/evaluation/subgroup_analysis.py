"""Subgroup performance analysis.

Groups predictions by a metadata column and reports metrics per subgroup. Small
subgroups are suppressed to avoid unstable or re-identifying statistics.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence

import numpy as np

from eyedx_ml.evaluation.evaluator import compute_label_metrics

__all__ = ["subgroup_metrics"]


def subgroup_metrics(
    groups: Sequence,
    y_true: np.ndarray,
    y_score: np.ndarray,
    *,
    metric_fn: Optional[Callable[..., Dict[str, Any]]] = None,
    threshold: Optional[float] = None,
    min_cell_size: int = 5,
) -> Dict[str, Any]:
    """Compute metrics per group.

    ``groups`` is a sequence of group labels aligned with ``y_true``/``y_score``
    (single label). Subgroups with fewer than ``min_cell_size`` members are
    reported with ``suppressed: True`` and no metrics.
    """
    groups = np.asarray(groups)
    y_true = np.asarray(y_true, dtype=float).ravel()
    y_score = np.asarray(y_score, dtype=float).ravel()
    if groups.shape[0] != y_true.shape[0]:
        raise ValueError("groups must align with y_true")

    fn = metric_fn or (lambda yt, ys: compute_label_metrics(yt, ys, threshold=threshold))
    result: Dict[str, Any] = {"min_cell_size": min_cell_size, "groups": {}}
    for value in sorted(set(groups.tolist()), key=lambda v: str(v)):
        mask = groups == value
        count = int(mask.sum())
        key = str(value)
        if count < min_cell_size:
            result["groups"][key] = {"count": count, "suppressed": True}
            continue
        result["groups"][key] = {
            "count": count,
            "suppressed": False,
            "metrics": fn(y_true[mask], y_score[mask]),
        }
    return result
