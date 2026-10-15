"""Learning-rate scheduler construction."""

from __future__ import annotations

from typing import Any, Mapping, Optional

from eyedx_ml.errors import DependencyError, NotConfiguredError

__all__ = ["build_scheduler", "build_scheduler_from_config"]


def _torch():
    try:
        import torch
    except Exception as exc:  # pragma: no cover - optional dependency
        raise DependencyError("torch is required to build schedulers") from exc
    return torch


def _warmup_lambda(optimizer, warmup_epochs: int, start_factor: float = 0.01):
    torch = _torch()
    warmup = torch.optim.lr_scheduler.LambdaLR(
        optimizer, lambda epoch: min(1.0, (epoch + 1) / max(1, warmup_epochs))
        if warmup_epochs > 0
        else 1.0
    )
    return warmup


def build_scheduler(
    optimizer,
    *,
    name: str = "cosine",
    epochs: int = 1,
    warmup_epochs: int = 0,
    min_lr: Optional[float] = None,
):
    """Build a scheduler by name. Returns ``None`` for ``name == "none"``."""
    torch = _torch()
    name = (name or "none").lower()
    if name == "none":
        return None
    if name == "step":
        return torch.optim.lr_scheduler.StepLR(optimizer, step_size=max(1, epochs // 3), gamma=0.1)
    if name == "cosine":
        if warmup_epochs > 0:
            warmup = _warmup_lambda(optimizer, warmup_epochs)
            cosine = torch.optim.lr_scheduler.CosineAnnealingLR(
                optimizer, T_max=max(1, epochs - warmup_epochs), eta_min=min_lr or 0.0
            )
            return torch.optim.lr_scheduler.SequentialLR(
                optimizer, schedulers=[warmup, cosine], milestones=[warmup_epochs]
            )
        return torch.optim.lr_scheduler.CosineAnnealingLR(
            optimizer, T_max=max(1, epochs), eta_min=min_lr or 0.0
        )
    if name == "onecycle":
        return torch.optim.lr_scheduler.OneCycleLR(
            optimizer, max_lr=optimizer.param_groups[0]["lr"], total_steps=max(1, epochs)
        )
    if name == "plateau":
        return torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="min")
    raise NotConfiguredError(f"unknown scheduler: {name}")


def build_scheduler_from_config(optimizer, config: Mapping[str, Any], epochs: int):
    cfg = dict(config or {})
    return build_scheduler(
        optimizer,
        name=cfg.get("name", "none"),
        epochs=epochs,
        warmup_epochs=int(cfg.get("warmup_epochs", 0)),
        min_lr=cfg.get("min_lr"),
    )
