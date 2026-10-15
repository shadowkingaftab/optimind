"""Error analysis: surfaced false positives / false negatives."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

import numpy as np

__all__ = ["error_cases", "error_summary"]


def error_cases(
    y_true: np.ndarray,
    y_score: np.ndarray,
    *,
    threshold: float,
    record_ids: Optional[Sequence] = None,
    max_cases: int = 100,
) -> Dict[str, List[Dict[str, Any]]]:
    """Return misclassified cases. Identifiers are returned only if provided by
    the caller (pseudonymous record ids); no patient data is derived here.
    """
    y_true = np.asarray(y_true, dtype=float).ravel()
    y_score = np.asarray(y_score, dtype=float).ravel()
    y_pred = (y_score >= threshold).astype(int)
    ids = list(record_ids) if record_ids is not None else [None] * y_true.size

    fps: List[Dict[str, Any]] = []
    fns: List[Dict[str, Any]] = []
    for i in range(y_true.size):
        entry = {"record_id": ids[i], "score": float(y_score[i]), "target": int(y_true[i])}
        if y_true[i] == 0 and y_pred[i] == 1:
            fps.append(entry)
        elif y_true[i] == 1 and y_pred[i] == 0:
            fns.append(entry)

    fps = sorted(fps, key=lambda e: e["score"], reverse=True)[:max_cases]
    fns = sorted(fns, key=lambda e: e["score"])[:max_cases]
    return {"false_positives": fps, "false_negatives": fns}


def error_summary(y_true: np.ndarray, y_score: np.ndarray, *, threshold: float) -> Dict[str, int]:
    cases = error_cases(y_true, y_score, threshold=threshold)
    return {
        "false_positives": len(cases["false_positives"]),
        "false_negatives": len(cases["false_negatives"]),
    }
