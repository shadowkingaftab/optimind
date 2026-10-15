"""Image validation and structural quality checks.

Decodes images with Pillow (an optional dependency) to verify format,
dimensions and a few heuristic quality signals. These signals are *not*
clinical measurements. Image bytes never leave this module and file paths are
never logged.

Quality thresholds are configuration inputs; defaults here match the backend
screening thresholds and must be reviewed per model.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Sequence, Union

from eyedx_ml.data.ingestion.dataset_importer import DatasetRecord
from eyedx_ml.data.validation.integrity_report import ValidationReport

__all__ = [
    "ImageError",
    "ImageQualityThresholds",
    "ImageProbe",
    "validate_image",
    "validate_image_records",
]

SUPPORTED_FORMATS = frozenset({"JPEG", "PNG"})


class ImageError(RuntimeError):
    """Raised when an image cannot be decoded (dependency missing or corrupt)."""


@dataclass(frozen=True)
class ImageQualityThresholds:
    min_width: int = 256
    min_height: int = 256
    min_brightness: float = 0.2
    max_blur_score: float = 0.3
    require_rgb: bool = False
    allowed_formats: Sequence[str] = tuple(SUPPORTED_FORMATS)

    def as_dict(self) -> Dict[str, object]:
        return {
            "min_width": self.min_width,
            "min_height": self.min_height,
            "min_brightness": self.min_brightness,
            "max_blur_score": self.max_blur_score,
            "require_rgb": self.require_rgb,
            "allowed_formats": list(self.allowed_formats),
        }


@dataclass(frozen=True)
class ImageProbe:
    width: int
    height: int
    mode: str
    format: str
    brightness: Optional[float] = None
    blur_score: Optional[float] = None
    readable: bool = True


def _load_pillow():
    try:  # pragma: no cover - optional dependency
        from PIL import Image, ImageFilter, ImageStat
    except Exception as exc:  # pragma: no cover
        raise ImageError(
            "Pillow is required to validate images; install it to run image checks"
        ) from exc
    return Image, ImageFilter, ImageStat


def probe_image(path: Union[str, Path]) -> ImageProbe:
    """Decode an image header and compute heuristic brightness/blur."""
    Image, ImageFilter, ImageStat = _load_pillow()
    file_path = Path(path)
    if not file_path.is_file():
        raise ImageError("image file not found")
    with Image.open(file_path) as image:
        fmt = (image.format or "").upper()
        width, height = image.size
        mode = image.mode
        gray = image.convert("L")
        brightness = ImageStat.Stat(gray).mean[0] / 255.0
        edges = gray.filter(ImageFilter.FIND_EDGES)
        variance = ImageStat.Stat(edges).var[0] if edges.size else 0.0
        blur_score = 1.0 / (1.0 + variance / 1000.0)
    return ImageProbe(
        width=width,
        height=height,
        mode=mode,
        format=fmt,
        brightness=brightness,
        blur_score=blur_score,
    )


def validate_image(
    path: Union[str, Path],
    *,
    thresholds: Optional[ImageQualityThresholds] = None,
    record_index: Optional[int] = None,
) -> ValidationReport:
    """Validate a single image; returns a report (never raises for quality)."""
    policy = thresholds or ImageQualityThresholds()
    report = ValidationReport(checked=1)
    ctx = {"index": record_index} if record_index is not None else {}

    try:
        probe = probe_image(path)
    except ImageError as exc:
        report.error("image_unreadable", str(exc), **ctx)
        return report

    if probe.format and probe.format not in policy.allowed_formats:
        report.error("unsupported_format", f"format not allowed: {probe.format}", **ctx)
    if probe.width < policy.min_width or probe.height < policy.min_height:
        report.warning(
            "low_resolution",
            "image below minimum resolution",
            width=probe.width,
            height=probe.height,
            **ctx,
        )
    if policy.require_rgb and probe.mode not in ("RGB", "L"):
        report.warning("unexpected_mode", f"mode is {probe.mode}", **ctx)
    if probe.brightness is not None and probe.brightness < policy.min_brightness:
        report.warning(
            "low_brightness", "image appears dark", brightness=probe.brightness, **ctx
        )
    if probe.blur_score is not None and probe.blur_score > policy.max_blur_score:
        report.warning(
            "possible_blur", "image may be blurred", blur_score=probe.blur_score, **ctx
        )
    return report


def validate_image_records(
    records: Sequence[DatasetRecord],
    *,
    image_root: Union[str, Path],
    thresholds: Optional[ImageQualityThresholds] = None,
    limit: Optional[int] = None,
) -> ValidationReport:
    """Validate images referenced by records, relative to ``image_root``."""
    root = Path(image_root)
    report = ValidationReport()
    selected = records if limit is None else records[:limit]
    for index, record in enumerate(selected):
        report.merge(
            validate_image(
                root / record.image_path,
                thresholds=thresholds,
                record_index=index,
            )
        )
    return report
