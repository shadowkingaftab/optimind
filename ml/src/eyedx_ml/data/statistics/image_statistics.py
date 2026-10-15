"""Image-level statistics.

Collects dimension, aspect-ratio, brightness and modality distributions from a
sample of images. Statistics are aggregate only; no pixel data or identifiers
are retained.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Union

from eyedx_ml.data.ingestion.dataset_importer import DatasetRecord
from eyedx_ml.data.validation.image_validator import ImageError, probe_image

__all__ = ["ImageStatistics", "compute_image_statistics"]


@dataclass
class ImageStatistics:
    attempted: int = 0
    readable: int = 0
    unreadable: int = 0
    width: Dict[str, float] = field(default_factory=dict)
    height: Dict[str, float] = field(default_factory=dict)
    aspect_ratio: Dict[str, float] = field(default_factory=dict)
    brightness: Dict[str, float] = field(default_factory=dict)
    formats: Dict[str, int] = field(default_factory=dict)
    modes: Dict[str, int] = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {
            "attempted": self.attempted,
            "readable": self.readable,
            "unreadable": self.unreadable,
            "width": self.width,
            "height": self.height,
            "aspect_ratio": self.aspect_ratio,
            "brightness": self.brightness,
            "formats": self.formats,
            "modes": self.modes,
        }


def _summary(values: Sequence[float]) -> Dict[str, float]:
    if not values:
        return {}
    ordered = sorted(values)
    n = len(ordered)

    def _pct(p: float) -> float:
        idx = p * (n - 1)
        lo = int(idx)
        hi = min(lo + 1, n - 1)
        return ordered[lo] + (ordered[hi] - ordered[lo]) * (idx - lo)

    return {
        "min": ordered[0],
        "max": ordered[-1],
        "mean": sum(ordered) / n,
        "median": _pct(0.5),
        "p05": _pct(0.05),
        "p95": _pct(0.95),
    }


def compute_image_statistics(
    records: Sequence[DatasetRecord],
    *,
    image_root: Union[str, Path],
    limit: Optional[int] = None,
) -> ImageStatistics:
    root = Path(image_root)
    stats = ImageStatistics()
    selected = records if limit is None else records[:limit]
    widths: List[float] = []
    heights: List[float] = []
    ratios: List[float] = []
    brightness: List[float] = []
    formats: Counter = Counter()
    modes: Counter = Counter()

    for record in selected:
        stats.attempted += 1
        try:
            probe = probe_image(root / record.image_path)
        except ImageError:
            stats.unreadable += 1
            continue
        stats.readable += 1
        widths.append(probe.width)
        heights.append(probe.height)
        if probe.height:
            ratios.append(probe.width / probe.height)
        if probe.brightness is not None:
            brightness.append(probe.brightness)
        formats[probe.format] += 1
        modes[probe.mode] += 1

    stats.width = _summary(widths)
    stats.height = _summary(heights)
    stats.aspect_ratio = _summary(ratios)
    stats.brightness = _summary(brightness)
    stats.formats = dict(formats)
    stats.modes = dict(modes)
    return stats
