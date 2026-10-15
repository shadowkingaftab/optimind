"""Deterministic stratified splitting (record level).

Uses a largest-remainder allocation per stratum so target ratios are respected
without depending on scikit-learn. Splitting is seeded and reproducible.
"""

from __future__ import annotations

import hashlib
import random
from typing import Dict, Iterable, List, Mapping, Sequence

__all__ = ["SplitError", "validate_ratios", "allocate_counts", "stratified_split"]


class SplitError(ValueError):
    """Raised for invalid ratios or impossible split requests."""


def validate_ratios(ratios: Mapping[str, float]) -> None:
    if not ratios:
        raise SplitError("ratios must not be empty")
    total = sum(ratios.values())
    if abs(total - 1.0) > 1e-6:
        raise SplitError(f"ratios must sum to 1.0 (got {total})")
    if any(v < 0 for v in ratios.values()):
        raise SplitError("ratios must be non-negative")


def _seeded_shuffle(items: List[str], seed: int, salt: str) -> List[str]:
    digest = hashlib.sha256(f"{seed}:{salt}".encode("utf-8")).hexdigest()
    rng = random.Random(int(digest[:16], 16))
    shuffled = list(items)
    rng.shuffle(shuffled)
    return shuffled


def allocate_counts(total: int, ratios: Mapping[str, float]) -> Dict[str, int]:
    """Allocate ``total`` items across splits using the largest remainder."""
    validate_ratios(ratios)
    names = list(ratios.keys())
    raw = {name: total * ratios[name] for name in names}
    counts = {name: int(raw[name]) for name in names}
    remainder = total - sum(counts.values())
    # Distribute the remainder by largest fractional part, ties by name order.
    order = sorted(names, key=lambda n: (raw[n] - counts[n], n), reverse=True)
    for i in range(remainder):
        counts[order[i % len(order)]] += 1
    return counts


def stratified_split(
    items_by_stratum: Mapping[str, Sequence[str]],
    ratios: Mapping[str, float],
    *,
    seed: int = 42,
) -> Dict[str, str]:
    """Assign every key to a split, stratifying within each stratum.

    Returns ``key -> split``. Each stratum is shuffled deterministically and
    allocated independently so class balance is preserved across splits.
    """
    validate_ratios(ratios)
    assignment: Dict[str, str] = {}
    for stratum, keys in items_by_stratum.items():
        unique_sorted = sorted(set(keys))
        if not unique_sorted:
            continue
        shuffled = _seeded_shuffle(unique_sorted, seed, stratum)
        counts = allocate_counts(len(shuffled), ratios)
        cursor = 0
        for split, count in counts.items():
            for key in shuffled[cursor : cursor + count]:
                assignment[key] = split
            cursor += count
    return assignment
