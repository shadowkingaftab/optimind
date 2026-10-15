"""Reliability diagram rendering."""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Sequence

import numpy as np

from eyedx_ml.errors import DependencyError
from eyedx_ml.metrics.calibration import reliability_curve

__all__ = ["reliability_data", "plot_reliability_diagram"]


def reliability_data(
    y_true: np.ndarray, y_prob: np.ndarray, *, n_bins: int = 10
):
    conf, acc, count = reliability_curve(y_true, y_prob, n_bins=n_bins)
    return [
        {"bin": i, "confidence": float(conf[i]), "accuracy": float(acc[i]), "count": int(count[i])}
        for i in range(len(count))
    ]


def plot_reliability_diagram(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    *,
    output_path: Optional[str] = None,
    n_bins: int = 10,
) -> str:
    """Render a reliability diagram to ``output_path``. Requires matplotlib."""
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as exc:  # pragma: no cover - optional dependency
        raise DependencyError(
            "matplotlib is required to plot reliability diagrams"
        ) from exc

    conf, acc, count = reliability_curve(y_true, y_prob, n_bins=n_bins)
    plt.figure(figsize=(5, 5))
    plt.plot([0, 1], [0, 1], linestyle="--", color="gray", label="perfect")
    plt.bar(conf, acc, width=1.0 / n_bins, alpha=0.6, edgecolor="black", label="model")
    plt.xlabel("predicted probability")
    plt.ylabel("observed frequency")
    plt.title("Reliability diagram")
    plt.legend(loc="upper left")
    path = Path(output_path or "reliability_diagram.png")
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(path, dpi=120)
    plt.close()
    return str(path)
