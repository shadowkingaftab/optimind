"""Composable preprocessing pipeline.

A pipeline is an ordered list of named steps. Steps are callables that take and
return a NumPy array (except the final normalise step, which returns float).
Pipelines can be built from a YAML/JSON mapping so preprocessing is declared in
config rather than code.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence, Tuple

import numpy as np

from .artifact_removal import mask_background, suppress_highlights
from .color_correction import gray_world, standardize_channels
from .crop_retina import center_crop, crop_retina
from .illumination_correction import correct_illumination
from .normalize import Normalize
from .resize import resize_image

__all__ = ["PipelineError", "PreprocessingPipeline", "resolve_step"]


class PipelineError(ValueError):
    """Raised for unknown steps or invalid step parameters."""


def resolve_step(name: str, params: Optional[Mapping[str, Any]] = None) -> Callable:
    """Instantiate a preprocessing step by name."""
    params = dict(params or {})

    def _size(value: Any) -> Optional[Tuple[int, int]]:
        if value is None:
            return None
        if isinstance(value, (list, tuple)) and len(value) == 2:
            return (int(value[0]), int(value[1]))
        raise PipelineError(f"size must be [width, height], got {value!r}")

    if name == "crop_retina":
        params["target_size"] = _size(params.get("target_size"))
        return lambda image: crop_retina(image, **params)
    if name == "center_crop":
        size = _size(params.get("size"))
        if size is None:
            raise PipelineError("center_crop requires size")
        return lambda image: center_crop(image, size)
    if name == "resize":
        size = _size(params.get("size"))
        if size is None:
            raise PipelineError("resize requires size")
        params["size"] = size
        return lambda image: resize_image(image, **params)
    if name == "illumination":
        return lambda image: correct_illumination(image, **params)
    if name == "gray_world":
        return lambda image: gray_world(image, **params)
    if name == "standardize_channels":
        return lambda image: standardize_channels(image, **params)
    if name == "mask_background":
        return lambda image: mask_background(image, **params)
    if name == "suppress_highlights":
        return lambda image: suppress_highlights(image, **params)
    if name == "normalize":
        return Normalize(**params)
    raise PipelineError(f"unknown preprocessing step: {name}")


@dataclass
class PreprocessingPipeline:
    steps: List[Tuple[str, Callable]] = field(default_factory=list)

    def add(self, name: str, step: Callable) -> "PreprocessingPipeline":
        self.steps.append((name, step))
        return self

    def __call__(self, image: np.ndarray) -> np.ndarray:
        result = image
        for _name, step in self.steps:
            result = step(result)
        return result

    def describe(self) -> List[str]:
        return [name for name, _ in self.steps]

    @classmethod
    def from_config(cls, config: Mapping[str, Any]) -> "PreprocessingPipeline":
        """Build from ``{"steps": [{"name": ..., "params": {...}}, ...]}``."""
        steps = config.get("steps")
        if not isinstance(steps, Sequence) or isinstance(steps, (str, bytes)):
            raise PipelineError("config must contain a 'steps' list")
        pipeline = cls()
        for entry in steps:
            if isinstance(entry, str):
                pipeline.add(entry, resolve_step(entry))
            elif isinstance(entry, Mapping):
                name = entry.get("name")
                if not name:
                    raise PipelineError("each step entry requires a 'name'")
                pipeline.add(name, resolve_step(str(name), entry.get("params")))
            else:
                raise PipelineError("step entries must be names or mappings")
        return pipeline
