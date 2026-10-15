"""Image quality gate for inference.

Applies structural quality checks (resolution, brightness, blur) before a model
runs. Thresholds come from the inference config and are INPUT_REQUIRED per model.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence

import numpy as np

__all__ = ["QualityResult", "QualityGate", "variance_of_laplacian"]


def _to_gray(image: np.ndarray) -> np.ndarray:
    image = np.asarray(image, dtype=float)
    if image.ndim == 3:
        image = image[..., :3].mean(axis=-1)
    if image.max() > 1.0:
        image = image / 255.0
    return image


def variance_of_laplacian(gray: np.ndarray) -> float:
    """Variance of a 4-neighbour Laplacian; higher means sharper."""
    gray = np.asarray(gray, dtype=float)
    kernel = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]], dtype=float)
    h, w = gray.shape
    lap = np.zeros_like(gray)
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            window = gray[y - 1 : y + 2, x - 1 : x + 2]
            lap[y, x] = float((window * kernel).sum())
    return float(lap.var())


@dataclass
class QualityResult:
    passed: bool
    reasons: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {"passed": self.passed, "reasons": list(self.reasons), "metrics": dict(self.metrics)}


class QualityGate:
    def __init__(
        self,
        *,
        min_resolution: Optional[int] = None,
        min_brightness: Optional[float] = None,
        max_blur_score: Optional[float] = None,
        expected_shape: Optional[Sequence[int]] = None,
    ) -> None:
        self.min_resolution = min_resolution
        self.min_brightness = min_brightness
        self.max_blur_score = max_blur_score
        self.expected_shape = tuple(expected_shape) if expected_shape else None

    def check(self, image: np.ndarray) -> QualityResult:
        image = np.asarray(image)
        reasons: List[str] = []
        metrics: Dict[str, Any] = {}

        height, width = image.shape[0], image.shape[1]
        metrics["height"] = int(height)
        metrics["width"] = int(width)
        if self.min_resolution is not None:
            metrics["min_resolution"] = int(self.min_resolution)
            if min(height, width) < self.min_resolution:
                reasons.append(
                    f"resolution {height}x{width} below minimum {self.min_resolution}"
                )

        gray = _to_gray(image)
        brightness = float(gray.mean())
        metrics["brightness"] = brightness
        if self.min_brightness is not None:
            metrics["min_brightness"] = float(self.min_brightness)
            if brightness < self.min_brightness:
                reasons.append(
                    f"brightness {brightness:.3f} below minimum {self.min_brightness}"
                )

        if self.max_blur_score is not None:
            sharpness = variance_of_laplacian(gray)
            # Normalise to a blurriness in [0,1]: lower sharpness -> higher score.
            blur_score = 1.0 / (1.0 + sharpness)
            metrics["blur_score"] = blur_score
            metrics["max_blur_score"] = float(self.max_blur_score)
            if blur_score > self.max_blur_score:
                reasons.append(
                    f"blur score {blur_score:.3f} above maximum {self.max_blur_score}"
                )

        return QualityResult(passed=not reasons, reasons=reasons, metrics=metrics)
