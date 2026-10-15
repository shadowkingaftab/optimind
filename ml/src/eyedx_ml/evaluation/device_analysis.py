"""Device-level performance analysis."""

from __future__ import annotations

from typing import Any, Dict, Optional, Sequence

import numpy as np

from eyedx_ml.evaluation.subgroup_analysis import subgroup_metrics

__all__ = ["device_metrics"]


def device_metrics(
    device_ids: Sequence,
    y_true: np.ndarray,
    y_score: np.ndarray,
    *,
    threshold: Optional[float] = None,
    min_cell_size: int = 5,
) -> Dict[str, Any]:
    return subgroup_metrics(
        device_ids, y_true, y_score, threshold=threshold, min_cell_size=min_cell_size
    )
