"""Checkpoint saving/loading with contract-aligned metadata."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Sequence, Union

from eyedx_ml.errors import ArtifactUnavailableError, DependencyError, NotConfiguredError

__all__ = [
    "build_checkpoint_metadata",
    "save_checkpoint",
    "load_checkpoint",
    "CheckpointManager",
]


def _torch():
    try:
        import torch
    except Exception as exc:  # pragma: no cover - optional dependency
        raise DependencyError("torch is required for checkpoints") from exc
    return torch


def build_checkpoint_metadata(
    *,
    model_id: str,
    model_version: str,
    architecture: str,
    backbone: Optional[str],
    labels: Sequence[str],
    preprocessing: Mapping[str, Any],
    capabilities: Optional[Mapping[str, Any]] = None,
    calibration: Optional[Mapping[str, Any]] = None,
    created_at: Optional[str] = None,
    extra: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """Build metadata matching ``contracts/json-schemas/model-metadata.schema.json``.

    ``labels`` and ``preprocessing`` are required by the contract; callers must
    supply approved values (INPUT_REQUIRED) rather than placeholders.
    """
    if not model_id or not model_version:
        raise NotConfiguredError("model_id and model_version are required")
    label_list = list(labels) if not isinstance(labels, Mapping) else list(labels)
    if not label_list:
        raise NotConfiguredError("approved labels are required (INPUT_REQUIRED)")
    if not preprocessing:
        raise NotConfiguredError("preprocessing descriptor is required")
    caps = dict(capabilities or {})
    for key in ("supports_uncertainty", "supports_explanation", "supports_abstention"):
        caps.setdefault(key, False)
    # The model-metadata schema forbids additional top-level properties, so
    # architecture/backbone/extra are tucked inside `capabilities`, which allows
    # additional properties.
    caps["architecture"] = architecture
    if backbone:
        caps["backbone"] = backbone
    if extra:
        caps["extra"] = dict(extra)
    metadata: Dict[str, Any] = {
        "model_id": model_id,
        "model_version": model_version,
        "created_at": created_at or datetime.now(timezone.utc).isoformat(),
        "labels": label_list,
        "preprocessing": dict(preprocessing),
        "capabilities": caps,
    }
    if calibration is not None:
        metadata["calibration"] = dict(calibration)
    return metadata


def save_checkpoint(
    path: Union[str, Path],
    *,
    model,
    metadata: Mapping[str, Any],
    optimizer=None,
    scheduler=None,
    epoch: Optional[int] = None,
    metrics: Optional[Mapping[str, Any]] = None,
) -> Path:
    """Save a checkpoint plus its metadata sidecar (``<path>.meta.json``)."""
    torch = _torch()
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict() if optimizer is not None else None,
        "scheduler_state_dict": scheduler.state_dict() if scheduler is not None else None,
        "epoch": epoch,
        "metrics": dict(metrics or {}),
        "metadata": dict(metadata),
    }
    torch.save(payload, path)
    meta_path = path.with_suffix(path.suffix + ".meta.json")
    meta_path.write_text(json.dumps(dict(metadata), indent=2), encoding="utf-8")
    return path


def load_checkpoint(
    path: Union[str, Path],
    *,
    model=None,
    optimizer=None,
    scheduler=None,
    map_location: str = "cpu",
) -> Dict[str, Any]:
    """Load a checkpoint, optionally restoring state into provided objects."""
    torch = _torch()
    path = Path(path)
    if not path.is_file():
        raise ArtifactUnavailableError(f"checkpoint not found: {path.name}")
    payload = torch.load(path, map_location=map_location)
    if model is not None and payload.get("model_state_dict") is not None:
        model.load_state_dict(payload["model_state_dict"])
    if optimizer is not None and payload.get("optimizer_state_dict") is not None:
        optimizer.load_state_dict(payload["optimizer_state_dict"])
    if scheduler is not None and payload.get("scheduler_state_dict") is not None:
        scheduler.load_state_dict(payload["scheduler_state_dict"])
    return payload


class CheckpointManager:
    """Save best/last checkpoints under an output directory."""

    def __init__(
        self,
        output_dir: Union[str, Path],
        *,
        save_best: bool = True,
        save_last: bool = True,
        monitor: str = "val_loss",
        mode: str = "min",
    ) -> None:
        self.output_dir = Path(output_dir)
        self.save_best = save_best
        self.save_last = save_last
        self.monitor = monitor
        self.mode = mode
        self.best_score: Optional[float] = None

    def _is_better(self, value: float) -> bool:
        if self.best_score is None:
            return True
        return value < self.best_score if self.mode == "min" else value > self.best_score

    def update(self, model, metadata, *, epoch, metrics, optimizer=None, scheduler=None):
        score = metrics.get(self.monitor)
        saved = []
        if self.save_last:
            saved.append(
                save_checkpoint(
                    self.output_dir / "last.pt",
                    model=model,
                    metadata=metadata,
                    optimizer=optimizer,
                    scheduler=scheduler,
                    epoch=epoch,
                    metrics=metrics,
                )
            )
        if self.save_best and score is not None and self._is_better(float(score)):
            self.best_score = float(score)
            saved.append(
                save_checkpoint(
                    self.output_dir / "best.pt",
                    model=model,
                    metadata=metadata,
                    optimizer=optimizer,
                    scheduler=scheduler,
                    epoch=epoch,
                    metrics=metrics,
                )
            )
        return saved
