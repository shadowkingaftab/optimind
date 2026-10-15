"""Validation loop."""

from __future__ import annotations

from typing import Any, Dict, Optional

from eyedx_ml.errors import DependencyError
from eyedx_ml.training.training_loop import unpack_batch

__all__ = ["validate"]


def _torch():
    try:
        import torch
    except Exception as exc:  # pragma: no cover - optional dependency
        raise DependencyError("torch is required for validation") from exc
    return torch


def validate(
    model,
    loader,
    criterion=None,
    *,
    device="cpu",
    epoch: Optional[int] = None,
    collect_outputs: bool = False,
    autocast=None,
) -> Dict[str, Any]:
    """Run a validation pass.

    Returns ``{"loss": float|None, "num_samples": int}`` and, when
    ``collect_outputs`` is True, the concatenated model outputs and targets for
    downstream metric computation.
    """
    torch = _torch()
    model.eval()
    outputs_all = []
    targets_all = []
    total_loss = 0.0
    num_batches = 0
    num_samples = 0

    with torch.no_grad():
        for batch in loader:
            inputs, targets = unpack_batch(batch)
            inputs = inputs.to(device, non_blocking=True)
            if torch.is_tensor(targets):
                targets = targets.to(device, non_blocking=True)
            context = autocast if autocast is not None else torch.autocast(
                device_type="cuda" if str(device).startswith("cuda") else "cpu",
                enabled=False,
            )
            with context:
                out = model(inputs)
                if criterion is not None:
                    loss = criterion(out, targets)
                    total_loss += float(loss.detach().item())
                    num_batches += 1
            if collect_outputs:
                outputs_all.append(out.detach().float().cpu())
                if torch.is_tensor(targets):
                    targets_all.append(targets.detach().cpu())
            num_samples += int(inputs.shape[0])

    result: Dict[str, Any] = {
        "loss": (total_loss / num_batches) if num_batches else None,
        "num_samples": num_samples,
        "epoch": epoch,
    }
    if collect_outputs:
        result["outputs"] = torch.cat(outputs_all) if outputs_all else None
        result["targets"] = torch.cat(targets_all) if targets_all else None
    return result
