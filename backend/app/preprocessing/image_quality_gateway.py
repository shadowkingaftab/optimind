"""Image quality gateway.

Computes structural quality signals (resolution, brightness, contrast and a
blur proxy) using Pillow only. Thresholds come from
:class:`~app.postprocessing.threshold_policy.ThresholdPolicy` and are
configuration inputs, not validated clinical cutoffs.

A low-quality image yields ``acceptable=False`` and no disease result is
produced for it.
"""

from __future__ import annotations

from typing import Any

from app.postprocessing.threshold_policy import ThresholdPolicy
from app.preprocessing.image_metadata import aspect_ratio
from app.preprocessing.preprocessing_contract import QualityResult


def _analyze(image: Any) -> dict[str, float]:
    from PIL import ImageFilter, ImageStat  # type: ignore

    grayscale = image.convert("L")
    stats = ImageStat.Stat(grayscale)
    brightness = float(stats.mean[0]) / 255.0 if stats.mean else 0.0
    contrast = float(stats.stddev[0]) / 255.0 if stats.stddev else 0.0

    edges = grayscale.filter(ImageFilter.FIND_EDGES)
    edge_stats = ImageStat.Stat(edges)
    edge_stddev = float(edge_stats.stddev[0]) / 255.0 if edge_stats.stddev else 0.0

    return {
        "brightness": round(brightness, 4),
        "contrast": round(contrast, 4),
        "edge_density": round(edge_stddev, 4),
    }


def assess_quality(
    image: Any, policy: ThresholdPolicy | None = None
) -> QualityResult:
    """Assess image quality and return a structured result."""
    p = policy or ThresholdPolicy()
    issues: list[str] = []

    width, height = image.size
    min_dim = min(int(width), int(height))
    if min_dim < p.min_resolution:
        issues.append("resolution_below_minimum")

    ar = aspect_ratio(int(width), int(height))
    if ar <= 0 or abs(ar - 1.0) > p.max_aspect_ratio_deviation:
        issues.append("aspect_ratio_out_of_range")

    try:
        metrics = _analyze(image)
    except Exception:  # noqa: BLE001 - analysis must not crash the request
        metrics = {}
        issues.append("quality_analysis_unavailable")

    if metrics:
        if metrics["brightness"] < p.min_brightness:
            issues.append("brightness_below_minimum")
        if metrics["edge_density"] < p.max_blur_score:
            issues.append("possible_blur")

    acceptable = not issues
    # Heuristic composite score; clearly not a validated clinical metric.
    score = None
    if metrics:
        score = round(
            min(
                1.0,
                (metrics["brightness"] + metrics["contrast"] + metrics["edge_density"])
                / 3.0,
            ),
            4,
        )

    return QualityResult(
        acceptable=acceptable,
        score=score,
        issues=issues,
        metrics=metrics,
    )
