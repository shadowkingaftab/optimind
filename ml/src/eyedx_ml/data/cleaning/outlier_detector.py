"""Outlier detection for image attributes.

Flags records whose dimensions fall outside a configurable robust range. The
detector reports outliers; it never silently removes them. No images are
downloaded or modified.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Sequence, Union

from eyedx_ml.data.ingestion.dataset_importer import DatasetRecord
from eyedx_ml.data.validation.image_validator import ImageError, probe_image

__all__ = ["OutlierResult", "detect_size_outliers"]


@dataclass
class OutlierResult:
    outliers: List[str] = field(default_factory=list)
    unreadable: List[str] = field(default_factory=list)
    widths: List[int] = field(default_factory=list)
    heights: List[int] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "outliers": len(self.outliers),
            "unreadable": len(self.unreadable),
            "width_range": (min(self.widths), max(self.widths)) if self.widths else None,
            "height_range": (min(self.heights), max(self.heights))
            if self.heights
            else None,
        }


def _quantile(values: Sequence[int], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = q * (len(ordered) - 1)
    lo = int(idx)
    hi = min(lo + 1, len(ordered) - 1)
    frac = idx - lo
    return ordered[lo] * (1 - frac) + ordered[hi] * frac


def detect_size_outliers(
    records: Sequence[DatasetRecord],
    *,
    image_root: Union[str, Path],
    iqr_factor: float = 1.5,
    min_dimension: Optional[int] = None,
) -> OutlierResult:
    """Flag images whose width/height are robust outliers (IQR rule)."""
    root = Path(image_root)
    result = OutlierResult()
    probes: List[tuple[str, int, int]] = []
    for record in records:
        try:
            probe = probe_image(root / record.image_path)
        except ImageError:
            result.unreadable.append(record.record_id)
            continue
        probes.append((record.record_id, probe.width, probe.height))

    widths = [w for _, w, _ in probes]
    heights = [h for _, _, h in probes]
    result.widths = widths
    result.heights = heights

    if not widths or not heights:
        return result

    w_q1, w_q3 = _quantile(widths, 0.25), _quantile(widths, 0.75)
    h_q1, h_q3 = _quantile(heights, 0.25), _quantile(heights, 0.75)
    w_low, w_high = w_q1 - iqr_factor * (w_q3 - w_q1), w_q3 + iqr_factor * (w_q3 - w_q1)
    h_low, h_high = h_q1 - iqr_factor * (h_q3 - h_q1), h_q3 + iqr_factor * (h_q3 - h_q1)

    for record_id, width, height in probes:
        if width < w_low or width > w_high or height < h_low or height > h_high:
            result.outliers.append(record_id)
        elif min_dimension is not None and (width < min_dimension or height < min_dimension):
            result.outliers.append(record_id)
    return result
