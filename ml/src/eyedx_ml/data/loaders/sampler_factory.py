"""Sampler factory.

Builds PyTorch samplers to address class imbalance. Weighted sampling is
computed from per-sample positive label counts; the sampler is deterministic
given a seed.
"""

from __future__ import annotations

from typing import Optional, Sequence

from eyedx_ml.data.loaders.image_dataset import ImageDataset, LoaderError, require_torch

__all__ = ["build_weighted_sampler", "build_balanced_sampler"]


def build_weighted_sampler(
    dataset: ImageDataset,
    *,
    power: float = 1.0,
    seed: Optional[int] = None,
):
    """Return a weighted sampler that up-weights rare positive labels.

    Weight for a sample is ``(sum of per-label inverse frequency) ** power``.
    Falls back to uniform weights when the dataset has no labels.
    """
    torch = require_torch()
    if not dataset.label_order:
        raise LoaderError("weighted sampling requires label_order on the dataset")

    matrix = dataset.label_matrix()  # (n, L)
    n, n_labels = matrix.shape
    if n == 0:
        raise LoaderError("cannot sample from an empty dataset")

    positives = matrix.sum(dim=0)
    weights_per_label = []
    for i in range(n_labels):
        pos = float(positives[i])
        neg = float(n - pos)
        if pos <= 0 or neg <= 0:
            weights_per_label.append(torch.ones(n, dtype=torch.double))
            continue
        imbalance = torch.where(
            matrix[:, i] >= 0.5,
            torch.full((n,), neg / max(pos, 1.0), dtype=torch.double),
            torch.full((n,), pos / max(neg, 1.0), dtype=torch.double),
        )
        weights_per_label.append(imbalance)

    stacked = torch.stack(weights_per_label, dim=0) if weights_per_label else None
    if stacked is None:
        sample_weights = torch.ones(n, dtype=torch.double)
    else:
        sample_weights = stacked.sum(dim=0).clamp(min=1e-6) ** power

    generator = None
    if seed is not None:
        generator = torch.Generator()
        generator.manual_seed(int(seed))
    return torch.utils.data.WeightedRandomSampler(
        sample_weights, num_samples=n, replacement=True, generator=generator
    )


def build_balanced_sampler(dataset: ImageDataset, *, seed: Optional[int] = None):
    """Alias for weighted sampling with a softened power."""
    return build_weighted_sampler(dataset, power=0.5, seed=seed)
