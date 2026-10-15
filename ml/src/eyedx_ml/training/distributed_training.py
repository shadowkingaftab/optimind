"""Distributed (DDP) training helpers.

All functions degrade gracefully to single-process behaviour when torch.distributed
is unavailable or ``enabled=False``. Cluster addresses/resources are supplied by
operations (INPUT_REQUIRED).
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Optional

from eyedx_ml.errors import DependencyError, NotConfiguredError

__all__ = ["DistributedContext", "setup_distributed"]


@dataclass
class DistributedContext:
    enabled: bool = False
    rank: int = 0
    local_rank: int = 0
    world_size: int = 1
    backend: Optional[str] = None
    initialized: bool = False

    @property
    def is_main(self) -> bool:
        return self.rank == 0


def setup_distributed(
    *,
    enabled: bool = False,
    backend: str = "nccl",
    world_size: Optional[Any] = None,
    master_addr: Optional[str] = None,
    master_port: Optional[Any] = None,
    local_rank_env: str = "LOCAL_RANK",
) -> DistributedContext:
    """Initialise the default process group when enabled.

    Returns a :class:`DistributedContext`. When ``enabled`` is False, returns a
    single-process context without importing torch.
    """
    if not enabled:
        return DistributedContext(enabled=False)

    if world_size in (None, "INPUT_REQUIRED"):
        raise NotConfiguredError(
            "distributed.world_size is INPUT_REQUIRED (set by the launcher)"
        )

    try:
        import torch
        import torch.distributed as dist
    except Exception as exc:  # pragma: no cover - optional dependency
        raise DependencyError("torch.distributed is required for distributed runs") from exc

    if not dist.is_available():
        raise DependencyError("torch.distributed is not available in this build")

    master_addr = master_addr or os.environ.get("MASTER_ADDR", "127.0.0.1")
    master_port = master_port or os.environ.get("MASTER_PORT")
    if master_port in (None, "INPUT_REQUIRED"):
        raise NotConfiguredError("distributed.master_port is INPUT_REQUIRED")

    os.environ.setdefault("MASTER_ADDR", str(master_addr))
    os.environ.setdefault("MASTER_PORT", str(master_port))

    local_rank = int(os.environ.get(local_rank_env, 0))
    if torch.cuda.is_available() and backend == "nccl":
        torch.cuda.set_device(local_rank)

    if not dist.is_initialized():
        dist.init_process_group(backend=backend)

    return DistributedContext(
        enabled=True,
        rank=dist.get_rank(),
        local_rank=local_rank,
        world_size=dist.get_world_size(),
        backend=backend,
        initialized=True,
    )


def wrap_model(model, context: DistributedContext):
    """Wrap a model in DDP when distributed; otherwise return it unchanged."""
    if not context.enabled:
        return model
    import torch

    device = torch.device("cuda", context.local_rank) if torch.cuda.is_available() else torch.device("cpu")
    model = model.to(device)
    return torch.nn.parallel.DistributedDataParallel(
        model, device_ids=[context.local_rank] if device.type == "cuda" else None
    )


def cleanup(context: Optional[DistributedContext] = None) -> None:
    if context is None or not context.initialized:
        return
    try:
        import torch.distributed as dist

        if dist.is_initialized():
            dist.destroy_process_group()
    except Exception:  # pragma: no cover
        pass
