"""Optimizer construction."""

from __future__ import annotations

from typing import Any, Mapping, Optional, Sequence

from eyedx_ml.errors import DependencyError, NotConfiguredError

__all__ = ["build_optimizer", "build_optimizer_from_config"]


def _torch():
    try:
        import torch
    except Exception as exc:  # pragma: no cover - optional dependency
        raise DependencyError("torch is required to build optimizers") from exc
    return torch


def build_optimizer(
    parameters,
    *,
    name: str = "adamw",
    lr: Optional[float] = None,
    weight_decay: float = 0.0,
    momentum: float = 0.9,
    betas: Sequence[float] = (0.9, 0.999),
):
    """Build an optimizer by name.

    ``lr`` is INPUT_REQUIRED; it must come from a training config / approved
    recipe, never a guessed default.
    """
    torch = _torch()
    if lr is None:
        raise NotConfiguredError("optimizer lr is required (INPUT_REQUIRED)")
    name = name.lower()
    if name == "adamw":
        return torch.optim.AdamW(parameters, lr=lr, weight_decay=weight_decay, betas=tuple(betas))
    if name == "adam":
        return torch.optim.Adam(parameters, lr=lr, weight_decay=weight_decay, betas=tuple(betas))
    if name == "sgd":
        return torch.optim.SGD(
            parameters, lr=lr, weight_decay=weight_decay, momentum=momentum
        )
    raise NotConfiguredError(f"unknown optimizer: {name}")


def build_optimizer_from_config(model, config: Mapping[str, Any]):
    cfg = dict(config or {})
    return build_optimizer(
        model.parameters(),
        name=cfg.get("name", "adamw"),
        lr=cfg.get("lr"),
        weight_decay=float(cfg.get("weight_decay", 0.0)),
        momentum=float(cfg.get("momentum", 0.9)),
        betas=cfg.get("betas", (0.9, 0.999)),
    )
