"""Heatmap normalisation and overlay utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple

import numpy as np

from eyedx_ml.errors import DependencyError

__all__ = ["normalize_heatmap", "overlay_heatmap", "save_heatmap", "resize_heatmap"]


def normalize_heatmap(heatmap: np.ndarray, *, eps: float = 1e-8) -> np.ndarray:
    heatmap = np.asarray(heatmap, dtype=float)
    lo, hi = float(heatmap.min()), float(heatmap.max())
    if hi - lo < eps:
        return np.zeros_like(heatmap)
    return (heatmap - lo) / (hi - lo)


def resize_heatmap(heatmap: np.ndarray, size: Tuple[int, int]) -> np.ndarray:
    """Nearest-neighbour resize of a 2D heatmap to (height, width)."""
    heatmap = np.asarray(heatmap, dtype=float)
    h, w = size
    ys = np.linspace(0, heatmap.shape[0] - 1, h).astype(int)
    xs = np.linspace(0, heatmap.shape[1] - 1, w).astype(int)
    return heatmap[np.ix_(ys, xs)]


def overlay_heatmap(
    image: np.ndarray,
    heatmap: np.ndarray,
    *,
    alpha: float = 0.4,
    colormap: str = "jet",
) -> np.ndarray:
    """Blend a heatmap over an RGB image (uint8 HxWx3). Requires matplotlib."""
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.cm as cm
    except Exception as exc:  # pragma: no cover - optional dependency
        raise DependencyError("matplotlib is required to overlay heatmaps") from exc

    image = np.asarray(image)
    if image.ndim == 2:
        image = np.stack([image] * 3, axis=-1)
    image = image.astype(float)
    if image.max() > 1.0:
        image = image / 255.0
    heatmap = normalize_heatmap(heatmap)
    heatmap = resize_heatmap(heatmap, image.shape[:2])
    cmap = cm.get_cmap(colormap)
    colored = cmap(heatmap)[..., :3]
    blended = (1 - alpha) * image + alpha * colored
    return np.clip(blended * 255.0, 0, 255).astype(np.uint8)


def save_heatmap(heatmap: np.ndarray, path: Optional[str] = None) -> str:
    """Save a heatmap as a PNG (RGB) using Pillow."""
    from PIL import Image

    heatmap = normalize_heatmap(heatmap)
    rgb = (heatmap * 255).astype(np.uint8)
    image = Image.fromarray(rgb, mode="L").convert("RGB")
    out = Path(path or "heatmap.png")
    out.parent.mkdir(parents=True, exist_ok=True)
    image.save(out)
    return str(out)
