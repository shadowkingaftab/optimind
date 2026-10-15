"""Evaluation report assembly and persistence."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Union

import numpy as np

__all__ = ["build_evaluation_report", "write_report"]


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    if isinstance(value, (np.floating, np.integer)):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    return value


def build_evaluation_report(
    metrics: Mapping[str, Any],
    *,
    split: str,
    model_id: Optional[str] = None,
    model_version: Optional[str] = None,
    dataset: Optional[str] = None,
    extra: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    report: Dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "split": split,
        "model_id": model_id,
        "model_version": model_version,
        "dataset": dataset,
        "metrics": _jsonable(dict(metrics)),
    }
    if extra:
        report["extra"] = _jsonable(dict(extra))
    return report


def write_report(report: Mapping[str, Any], path: Union[str, Path]) -> str:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_jsonable(dict(report)), indent=2), encoding="utf-8")
    return str(path)
