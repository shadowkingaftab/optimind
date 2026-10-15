"""Site-level performance analysis."""

from __future__ import annotations

from typing import Any, Callable, Dict, Mapping, Optional, Sequence

import numpy as np

from eyedx_ml.evaluation.subgroup_analysis import subgroup_metrics

__all__ = ["site_metrics", "site_consistency"]


def site_metrics(
    site_ids: Sequence,
    y_true: np.ndarray,
    y_score: np.ndarray,
    *,
    threshold: Optional[float] = None,
    min_cell_size: int = 5,
) -> Dict[str, Any]:
    return subgroup_metrics(
        site_ids, y_true, y_score, threshold=threshold, min_cell_size=min_cell_size
    )


def site_consistency(site_result: Mapping[str, Any], *, metric: str = "auroc") -> Dict[str, Any]:
    """Summarise spread of a metric across sites (only non-suppressed groups)."""
    values = []
    for name, entry in (site_result.get("groups") or {}).items():
        if entry.get("suppressed"):
            continue
        value = (entry.get("metrics") or {}).get(metric)
        if isinstance(value, (int, float)) and not np.isnan(value):
            values.append(float(value))
    if not values:
        return {"metric": metric, "sites": 0}
    return {
        "metric": metric,
        "sites": len(values),
        "min": float(min(values)),
        "max": float(max(values)),
        "range": float(max(values) - min(values)),
        "mean": float(np.mean(values)),
    }
