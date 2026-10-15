"""External validation.

Evaluates a frozen model and frozen operating thresholds on an external cohort.
External data must never be used to tune thresholds or select checkpoints.
"""

from __future__ import annotations

from typing import Any, Dict, Mapping, Optional, Sequence

import numpy as np

from eyedx_ml.evaluation.evaluator import Evaluator
from eyedx_ml.evaluation.evaluation_report import build_evaluation_report

__all__ = ["run_external_validation"]


def run_external_validation(
    y_true: np.ndarray,
    y_score: np.ndarray,
    *,
    labels: Sequence[str],
    thresholds: Optional[Mapping[str, float]] = None,
    model_id: Optional[str] = None,
    model_version: Optional[str] = None,
    dataset: Optional[str] = None,
    bootstrap: bool = True,
    n_resamples: int = 1000,
    confidence_level: float = 0.95,
    seed: int = 42,
) -> Dict[str, Any]:
    """Evaluate on an external cohort with frozen thresholds.

    When ``thresholds`` is empty/None, only threshold-free metrics are produced
    and a note is added. Thresholds must originate from internal validation.
    """
    evaluator = Evaluator(
        labels,
        thresholds=thresholds,
        bootstrap=bootstrap,
        n_resamples=n_resamples,
        confidence_level=confidence_level,
        seed=seed,
    )
    metrics = evaluator.evaluate(y_true, y_score)
    extra = {}
    if not thresholds:
        extra["note"] = (
            "no frozen thresholds supplied; threshold-based metrics omitted "
            "(INPUT_REQUIRED: approval of internal operating points)"
        )
    return build_evaluation_report(
        metrics,
        split="external",
        model_id=model_id,
        model_version=model_version,
        dataset=dataset,
        extra=extra,
    )
