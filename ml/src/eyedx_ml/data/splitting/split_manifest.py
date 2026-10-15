"""Split manifest persistence.

A split manifest is the reproducible record of how records were assigned to
cohorts. It stores per-record and per-patient assignments, the seed, target
ratios and input checksum so any split can be reproduced and audited. Patient
keys are pseudonymous.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Union

from eyedx_ml.data.ingestion.dataset_importer import DatasetRecord
from eyedx_ml.utils.file_hash import sha256_bytes

__all__ = ["SplitManifest", "write_split_csvs", "build_split_manifest"]


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class SplitManifest:
    version: str = "1.0.0"
    seed: int = 42
    ratios: Dict[str, float] = field(default_factory=dict)
    record_split: Dict[str, str] = field(default_factory=dict)
    patient_split: Dict[str, str] = field(default_factory=dict)
    split_counts: Dict[str, Dict[str, int]] = field(default_factory=dict)
    input_checksum: Optional[str] = None
    created_at: Optional[datetime] = None
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "seed": self.seed,
            "ratios": dict(self.ratios),
            "record_split": dict(self.record_split),
            "patient_split": dict(self.patient_split),
            "split_counts": {k: dict(v) for k, v in self.split_counts.items()},
            "input_checksum": self.input_checksum,
            "created_at": (self.created_at or _utcnow()).isoformat(),
            "notes": self.notes,
        }

    def write(self, path: Union[str, Path]) -> None:
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(
            json.dumps(self.to_dict(), indent=2, sort_keys=True), encoding="utf-8"
        )

    @classmethod
    def read(cls, path: Union[str, Path]) -> "SplitManifest":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        created = payload.get("created_at")
        return cls(
            version=str(payload.get("version", "1.0.0")),
            seed=int(payload.get("seed", 42)),
            ratios={
                str(k): float(v) for k, v in (payload.get("ratios") or {}).items()
            },
            record_split=dict(payload.get("record_split") or {}),
            patient_split=dict(payload.get("patient_split") or {}),
            split_counts=dict(payload.get("split_counts") or {}),
            input_checksum=payload.get("input_checksum"),
            created_at=datetime.fromisoformat(created) if created else None,
            notes=payload.get("notes"),
        )


def _manifest_checksum(records: Sequence[DatasetRecord]) -> str:
    rows = "\n".join(
        sorted(f"{r.record_id}|{r.image_path}|{r.patient_key}" for r in records)
    )
    return sha256_bytes(rows.encode("utf-8"))


def build_split_manifest(
    records: Sequence[DatasetRecord],
    record_split: Mapping[str, str],
    patient_split: Mapping[str, str],
    *,
    ratios: Mapping[str, float],
    seed: int = 42,
    version: str = "1.0.0",
    notes: Optional[str] = None,
) -> SplitManifest:
    """Assemble a manifest and compute per-split counts."""
    by_record = {r.record_id: r for r in records}
    counts: Dict[str, Dict[str, int]] = {}
    for record_id, split in record_split.items():
        entry = counts.setdefault(split, {"records": 0, "patients": 0})
        entry["records"] += 1
    for split in counts:
        patients = {
            by_record[rid].patient_key
            for rid, sp in record_split.items()
            if sp == split and rid in by_record
        }
        counts[split]["patients"] = len(patients)

    return SplitManifest(
        version=version,
        seed=seed,
        ratios=dict(ratios),
        record_split=dict(record_split),
        patient_split=dict(patient_split),
        split_counts=counts,
        input_checksum=_manifest_checksum(records),
        created_at=_utcnow(),
        notes=notes,
    )


def write_split_csvs(
    output_dir: Union[str, Path],
    records: Sequence[DatasetRecord],
    record_split: Mapping[str, str],
) -> List[Path]:
    """Write one CSV per split (record_id, image_path, patient_key, labels)."""
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    by_record = {r.record_id: r for r in records}
    partitions: Dict[str, List[str]] = {}
    for record_id, split in record_split.items():
        partitions.setdefault(split, []).append(record_id)

    written: List[Path] = []
    for split, ids in sorted(partitions.items()):
        path = directory / f"{split}.csv"
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["record_id", "image_path", "patient_key", "labels"])
            for record_id in sorted(ids):
                record = by_record.get(record_id)
                if record is None:
                    continue
                writer.writerow(
                    [
                        record.record_id,
                        record.image_path,
                        record.patient_key,
                        json.dumps(record.labels, sort_keys=True),
                    ]
                )
        written.append(path)
    return written
