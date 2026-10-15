"""Device selection for ML workloads.

PyTorch is an optional dependency; when unavailable a CPU placeholder is
returned and callers can decide whether to fail. No GPU is assumed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

__all__ = ["DeviceInfo", "select_device"]


@dataclass(frozen=True)
class DeviceInfo:
    kind: str  # "cpu" | "cuda" | "mps" | "unavailable"
    index: Optional[int] = None
    name: Optional[str] = None
    available: bool = True

    def as_str(self) -> str:
        if self.kind == "cuda" and self.index is not None:
            return f"cuda:{self.index}"
        return self.kind


def select_device(prefer: str = "auto") -> DeviceInfo:
    """Select a compute device.

    ``prefer`` is one of ``auto``, ``cpu``, ``cuda``, ``mps``. When PyTorch is
    not installed only ``cpu``/``unavailable`` are returned.
    """
    prefer = (prefer or "auto").lower()

    try:  # pragma: no cover - optional dependency
        import torch
    except Exception:
        if prefer in ("cpu", "auto"):
            return DeviceInfo(kind="cpu", available=True)
        return DeviceInfo(kind="unavailable", available=False)

    if prefer == "cpu":
        return DeviceInfo(kind="cpu", available=True)

    if prefer in ("auto", "cuda") and torch.cuda.is_available():
        index = 0 if prefer == "auto" else int(prefer.split(":")[-1])
        try:
            name = torch.cuda.get_device_name(index)
        except Exception:
            name = None
        return DeviceInfo(kind="cuda", index=index, name=name, available=True)

    mps = getattr(torch.backends, "mps", None)
    if prefer in ("auto", "mps") and mps is not None and mps.is_available():
        return DeviceInfo(kind="mps", available=True)

    if prefer == "auto":
        return DeviceInfo(kind="cpu", available=True)
    return DeviceInfo(kind="unavailable", available=False)
