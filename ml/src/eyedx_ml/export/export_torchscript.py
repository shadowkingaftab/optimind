"""TorchScript export."""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Union

from eyedx_ml.errors import DependencyError, ExportError

__all__ = ["export_torchscript", "load_torchscript"]


def _torch():
    try:
        import torch
    except Exception as exc:  # pragma: no cover - optional dependency
        raise DependencyError("torch is required for TorchScript export") from exc
    return torch


def export_torchscript(
    model,
    example_input,
    path: Union[str, Path],
    *,
    method: str = "trace",
    strict: bool = False,
) -> str:
    """Export a model to TorchScript via tracing or scripting."""
    torch = _torch()
    model.eval()
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with torch.no_grad():
            if method == "script":
                scripted = torch.jit.script(model)
            elif method == "trace":
                scripted = torch.jit.trace(model, example_input, strict=strict)
            else:
                raise ExportError(f"unknown TorchScript method: {method}")
    except Exception as exc:  # pragma: no cover - depends on model
        raise ExportError(f"TorchScript export failed: {exc}") from exc
    scripted.save(str(path))
    return str(path)


def load_torchscript(path: Union[str, Path]):
    torch = _torch()
    path = Path(path)
    if not path.is_file():
        raise ExportError(f"TorchScript file not found: {path.name}")
    return torch.jit.load(str(path))
