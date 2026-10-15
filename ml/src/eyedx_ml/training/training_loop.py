"""Single-epoch training loop."""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional

from eyedx_ml.errors import DependencyError

__all__ = ["train_epoch", "unpack_batch"]


def _torch():
    try:
        import torch
    except Exception as exc:  # pragma: no cover - optional dependency
        raise DependencyError("torch is required for training") from exc
    return torch


def unpack_batch(batch):
    """Return ``(inputs, targets)`` from common batch layouts."""
    if isinstance(batch, dict):
        inputs = batch.get("image", batch.get("images", batch.get("inputs")))
        targets = batch.get("labels", batch.get("target", batch.get("targets")))
        return inputs, targets
    if isinstance(batch, (list, tuple)) and len(batch) == 2:
        return batch[0], batch[1]
    raise ValueError("unsupported batch layout; expected (inputs, targets) or dict")


def train_epoch(
    model,
    loader,
    optimizer,
    criterion,
    *,
    device="cpu",
    epoch: int = 0,
    grad_accum_steps: int = 1,
    grad_clip_norm: Optional[float] = None,
    scaler=None,
    autocast=None,
    on_step: Optional[Callable[[int, float], None]] = None,
) -> Dict[str, Any]:
    """Run one training epoch and return aggregate loss statistics.

    Losses are computed from the supplied criterion; no metrics are fabricated.
    """
    torch = _torch()
    model.train()
    total_loss = 0.0
    num_batches = 0
    optimizer.zero_grad(set_to_none=True)

    for step, batch in enumerate(loader):
        inputs, targets = unpack_batch(batch)
        inputs = inputs.to(device, non_blocking=True)
        if torch.is_tensor(targets):
            targets = targets.to(device, non_blocking=True)

        context = autocast if autocast is not None else torch.autocast(
            device_type="cuda" if str(device).startswith("cuda") else "cpu", enabled=False
        )
        with context:
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            loss = loss / max(1, grad_accum_steps)

        if scaler is not None:
            scaler.scale(loss).backward()
        else:
            loss.backward()

        if (step + 1) % max(1, grad_accum_steps) == 0:
            if scaler is not None:
                if grad_clip_norm:
                    scaler.unscale_(optimizer)
                    torch.nn.utils.clip_grad_norm_(model.parameters(), grad_clip_norm)
                scaler.step(optimizer)
                scaler.update()
            else:
                if grad_clip_norm:
                    torch.nn.utils.clip_grad_norm_(model.parameters(), grad_clip_norm)
                optimizer.step()
            optimizer.zero_grad(set_to_none=True)

        step_loss = float(loss.detach().item()) * max(1, grad_accum_steps)
        total_loss += step_loss
        num_batches += 1
        if on_step is not None:
            on_step(step, step_loss)

    mean_loss = total_loss / num_batches if num_batches else float("nan")
    return {"loss": mean_loss, "steps": num_batches, "epoch": epoch}
