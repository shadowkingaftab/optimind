"""Multi-task loss combiner."""

from __future__ import annotations

from typing import Any, Callable, Dict, Mapping, Optional

from eyedx_ml.errors import DependencyError, NotConfiguredError

__all__ = ["MultiTaskLoss", "combine"]


def _torch():
    try:
        import torch
    except Exception as exc:  # pragma: no cover - optional dependency
        raise DependencyError("torch is required for losses") from exc
    return torch


class MultiTaskLoss:
    """Weighted sum of per-task losses.

    ``losses`` maps task name -> callable(logits, targets) -> scalar.
    ``weights`` maps task name -> weight; missing tasks default to 1.0.
    Task targets are supplied per task. Weights are INPUT_REQUIRED tuning choices.
    """

    def __new__(
        cls,
        losses: Mapping[str, Callable],
        weights: Optional[Mapping[str, float]] = None,
    ):
        torch = _torch()
        if not losses:
            raise NotConfiguredError("MultiTaskLoss requires at least one loss")

        class _MultiTaskLoss(torch.nn.Module):
            def __init__(self) -> None:
                super().__init__()
                self.losses = dict(losses)
                self.weights = {k: float((weights or {}).get(k, 1.0)) for k in losses}

            def forward(self, outputs: Mapping[str, Any], targets: Mapping[str, Any]):
                total = None
                parts: Dict[str, object] = {}
                for name, fn in self.losses.items():
                    if name not in outputs or name not in targets:
                        raise NotConfiguredError(
                            f"missing outputs/targets for task {name!r}"
                        )
                    value = fn(outputs[name], targets[name]) * self.weights[name]
                    parts[name] = value
                    total = value if total is None else total + value
                return total, parts

        return _MultiTaskLoss()


def combine(parts: Mapping[str, object], weights: Optional[Mapping[str, float]] = None):
    """Weighted sum of already-computed scalar losses."""
    total = None
    for name, value in parts.items():
        weight = float((weights or {}).get(name, 1.0))
        total = value * weight if total is None else total + value * weight
    return total
