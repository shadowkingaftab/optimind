"""DataLoader factory.

Centralises DataLoader construction so batching, shuffling and worker settings
are consistent and reproducible. ``shuffle`` and ``sampler`` are mutually
exclusive, matching PyTorch semantics.
"""

from __future__ import annotations

from typing import Optional

from eyedx_ml.data.loaders.image_dataset import LoaderError, require_torch

__all__ = ["build_dataloader"]


def build_dataloader(
    dataset,
    *,
    batch_size: int = 16,
    shuffle: bool = False,
    sampler=None,
    num_workers: int = 0,
    seed: Optional[int] = None,
    drop_last: bool = False,
    pin_memory: bool = False,
    persistent_workers: bool = False,
):
    """Construct a deterministic ``torch.utils.data.DataLoader``."""
    torch = require_torch()
    if batch_size <= 0:
        raise LoaderError("batch_size must be positive")
    if shuffle and sampler is not None:
        raise LoaderError("pass either shuffle=True or a sampler, not both")

    generator = None
    if seed is not None:
        generator = torch.Generator()
        generator.manual_seed(int(seed))

    kwargs = dict(
        batch_size=batch_size,
        shuffle=shuffle,
        sampler=sampler,
        num_workers=num_workers,
        drop_last=drop_last,
        pin_memory=pin_memory,
    )
    if generator is not None:
        kwargs["generator"] = generator
    if num_workers > 0:
        kwargs["persistent_workers"] = persistent_workers

    return torch.utils.data.DataLoader(dataset, **kwargs)
