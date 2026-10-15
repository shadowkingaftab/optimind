"""ONNX export."""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Sequence, Union

from eyedx_ml.errors import DependencyError, ExportError

__all__ = ["export_onnx", "onnx_available"]


def _torch():
    try:
        import torch
    except Exception as exc:  # pragma: no cover - optional dependency
        raise DependencyError("torch is required for ONNX export") from exc
    return torch


def onnx_available() -> bool:
    try:
        import onnx  # noqa: F401

        return True
    except Exception:
        return False


def export_onnx(
    model,
    example_input,
    path: Union[str, Path],
    *,
    input_names: Sequence[str] = ("input",),
    output_names: Sequence[str] = ("logits",),
    dynamic_axes: Optional[dict] = None,
    opset_version: int = 17,
) -> str:
    """Export a model to ONNX."""
    torch = _torch()
    if not onnx_available():
        raise DependencyError(
            "onnx is required for ONNX export (pip install onnx)"
        )
    model.eval()
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        torch.onnx.export(
            model,
            example_input,
            str(path),
            input_names=list(input_names),
            output_names=list(output_names),
            dynamic_axes=dynamic_axes,
            opset_version=opset_version,
        )
    except Exception as exc:  # pragma: no cover - depends on model
        raise ExportError(f"ONNX export failed: {exc}") from exc
    return str(path)
