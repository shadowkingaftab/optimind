"""Bootstrap confidence intervals."""

from __future__ import annotations

from typing import Callable, Dict, Optional, Tuple

import numpy as np

__all__ = ["bootstrap_ci"]


def bootstrap_ci(
    metric_fn: Callable[[np.ndarray, np.ndarray], Optional[float]],
    y_true: np.ndarray,
    y_score: np.ndarray,
    *,
    n_resamples: int = 1000,
    confidence_level: float = 0.95,
    seed: Optional[int] = 42,
) -> Dict[str, Optional[float]]:
    """Percentile bootstrap CI for a metric.

    Resampling is over samples (patient-level resampling is the caller's
    responsibility for grouped data). Returns point estimate and interval bounds.
    """
    y_true = np.asarray(y_true)
    y_score = np.asarray(y_score)
    n = y_true.shape[0]
    rng = np.random.default_rng(seed)
    point = metric_fn(y_true, y_score)

    estimates = []
    for _ in range(int(n_resamples)):
        idx = rng.integers(0, n, size=n)
        value = metric_fn(y_true[idx], y_score[idx])
        if value is not None and not (isinstance(value, float) and np.isnan(value)):
            estimates.append(float(value))

    if not estimates:
        return {"point": point, "lower": None, "upper": None, "n_resamples": 0}

    alpha = 1.0 - confidence_level
    lower = float(np.percentile(estimates, 100 * alpha / 2))
    upper = float(np.percentile(estimates, 100 * (1 - alpha / 2)))
    return {
        "point": point,
        "lower": lower,
        "upper": upper,
        "n_resamples": len(estimates),
        "confidence_level": confidence_level,
    }
