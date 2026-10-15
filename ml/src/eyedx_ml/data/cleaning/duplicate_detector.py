"""Duplicate detection.

Exact duplicates are found via checksum; near-duplicates via a difference hash
(dHash) computed with Pillow. When duplicates are found the earliest record in a
stable ordering is kept and the rest marked as duplicates, deterministically.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple, Union

from eyedx_ml.data.ingestion.dataset_importer import DatasetRecord

__all__ = ["DuplicateGroup", "find_exact_duplicates", "find_near_duplicates", "compute_dhash"]


@dataclass
class DuplicateGroup:
    keep: str
    duplicates: List[str] = field(default_factory=list)
    kind: str = "exact"

    def as_dict(self) -> Dict[str, object]:
        return {"keep": self.keep, "duplicates": list(self.duplicates), "kind": self.kind}


def find_exact_duplicates(records: Sequence[DatasetRecord]) -> List[DuplicateGroup]:
    """Group records sharing the same checksum (requires checksum_sha256)."""
    by_checksum: Dict[str, List[str]] = defaultdict(list)
    for record in records:
        if record.checksum_sha256:
            by_checksum[record.checksum_sha256].append(record.record_id)

    groups: List[DuplicateGroup] = []
    for ids in by_checksum.values():
        if len(ids) > 1:
            ordered = sorted(ids)
            groups.append(DuplicateGroup(keep=ordered[0], duplicates=ordered[1:], kind="exact"))
    return groups


def compute_dhash(path: Union[str, Path], *, hash_size: int = 8) -> Optional[str]:
    """Compute a dHash hex string, or ``None`` when Pillow is unavailable."""
    try:  # pragma: no cover - optional dependency
        from PIL import Image
    except Exception:
        return None
    file_path = Path(path)
    if not file_path.is_file():
        return None
    with Image.open(file_path) as image:
        small = image.convert("L").resize(
            (hash_size + 1, hash_size), Image.Resampling.LANCZOS
        )
        pixels = list(small.getdata())
    bits = 0
    bit_index = 0
    for row in range(hash_size):
        for col in range(hash_size):
            left = pixels[row * (hash_size + 1) + col]
            right = pixels[row * (hash_size + 1) + col + 1]
            if left > right:
                bits |= 1 << bit_index
            bit_index += 1
    return f"{bits:0{hash_size * hash_size // 4}x}"


def _hamming(a: str, b: str) -> int:
    return bin(int(a, 16) ^ int(b, 16)).count("1")


def find_near_duplicates(
    records: Sequence[DatasetRecord],
    *,
    image_root: Union[str, Path],
    max_distance: int = 2,
) -> List[DuplicateGroup]:
    """Find near-duplicate images by dHash within ``max_distance`` bits."""
    root = Path(image_root)
    hashes: Dict[str, str] = {}
    for record in records:
        digest = compute_dhash(root / record.image_path)
        if digest:
            hashes[record.record_id] = digest

    assigned: set[str] = set()
    groups: List[DuplicateGroup] = []
    ordered_ids = sorted(hashes)
    for i, left_id in enumerate(ordered_ids):
        if left_id in assigned:
            continue
        duplicates: List[str] = []
        for right_id in ordered_ids[i + 1 :]:
            if right_id in assigned:
                continue
            if _hamming(hashes[left_id], hashes[right_id]) <= max_distance:
                duplicates.append(right_id)
                assigned.add(right_id)
        if duplicates:
            assigned.add(left_id)
            groups.append(
                DuplicateGroup(keep=left_id, duplicates=duplicates, kind="near")
            )
    return groups
