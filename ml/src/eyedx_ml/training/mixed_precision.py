"""Mixed-precision (autocast / GradScaler) helpers."""

from __future__ import annotations

import contextlib

from typing import Optional

from eyedx_ml.errors import DependencyError, NotConfiguredError

__all__ = ["autocast", "make_grad_scaler", "resolve_amp"]


def _torch():
    try:
        import torch
    except Exception as exc:  # pragma: no cover - optional dependency
        raise DependencyError("torch is required for mixed precision") from exc
    return torch


def resolve_amp(enabled: bool, device: Optional[str] = None, *, allow_cpu: bool = False) -> bool:
    """Return whether AMP is usable.

    Mixed precision is disabled unless a CUDA device is available (unless
    ``allow_cpu``). Requesting AMP without a compatible device raises so a run
    never silently changes numerics.
    """
    torch = _torch()
    if not enabled:
        return False
    is_cuda = (device or "").startswith("cuda") or (
        device in (None, "auto") and torch.cuda.is_available()
    )
    if not is_cuda and not allow_cpu:
        raise NotConfiguredError(
            "mixed_precision requested but no CUDA device is available "
            "(INPUT_REQUIRED: compatible GPU); disable AMP or provide GPU"
        )
    return True


def autocast(device_type: str, enabled: bool):
    torch = _torch()
    if not enabled:
        return contextlib.nullcontext()
    if hasattr(torch, "autocast"):
        return torch.autocast(device_type=device_type, enabled=enabled)
    return contextlib.nullcontext()  # pragma: no cover - old torch


def make_grad_scaler(enabled: bool):
    """Return a GradScaler. On CPU (or disabled) returns a passthrough scaler."""
    torch = _torch()
    try:
        return torch.amp.GradScaler("cuda", enabled=enabled)
    except Exception:
        try:
            return torch.cuda.amp.GradScaler(enabled=enabled)  # pragma: no cover
        except Exception:
            return None
