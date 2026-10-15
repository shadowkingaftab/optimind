"""Annotation (label) import and mapping.

Labels are never invented: a label map must be explicitly approved by the
clinical owner. The map translates raw source label values into canonical codes
and declares which values to ignore. Applying an unapproved or empty map raises
immediately.

``labels.csv`` columns: ``record_id``, ``raw_label`` and either ``value`` (0/1
or score) or ``label_present`` (truthy). Multiple rows per record express
multi-label annotations.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Union

from eyedx_ml.data.ingestion.dataset_importer import DatasetRecord

__all__ = [
    "AnnotationError",
    "LabelDefinition",
    "LabelMap",
    "load_label_map",
    "load_annotations",
    "apply_label_map",
    "attach_labels",
]


class AnnotationError(ValueError):
    """Raised for missing/ambiguous labels or unapproved label maps."""


@dataclass(frozen=True)
class LabelDefinition:
    code: str
    display_name: str = ""
    source_values: Sequence[str] = field(default_factory=tuple)
    is_normal: bool = False
    description: Optional[str] = None

    def validate(self) -> None:
        if not self.code or " " in self.code:
            raise AnnotationError(f"invalid canonical label code: {self.code!r}")


@dataclass
class LabelMap:
    schema_version: str = "1.0.0"
    status: str = "INPUT_REQUIRED"
    labels: List[LabelDefinition] = field(default_factory=list)
    ignore_values: Sequence[str] = field(default_factory=tuple)
    notes: Optional[str] = None

    def validate_approved(self) -> None:
        if self.status != "approved":
            raise AnnotationError(
                "label map is not approved; a clinical owner must supply it "
                f"(status={self.status})"
            )
        if not self.labels:
            raise AnnotationError("approved label map contains no labels")
        for definition in self.labels:
            definition.validate()

    def build_lookup(self) -> Dict[str, str]:
        lookup: Dict[str, str] = {}
        for definition in self.labels:
            for value in definition.source_values:
                key = str(value).strip().lower()
                if key in lookup and lookup[key] != definition.code:
                    raise AnnotationError(f"source value mapped twice: {value}")
                lookup[key] = definition.code
        return lookup

    def codes(self) -> List[str]:
        return [d.code for d in self.labels]

    def to_dict(self) -> Dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "status": self.status,
            "labels": [
                {
                    "code": d.code,
                    "display_name": d.display_name,
                    "source_values": list(d.source_values),
                    "is_normal": d.is_normal,
                    "description": d.description,
                }
                for d in self.labels
            ],
            "ignore_values": list(self.ignore_values),
            "notes": self.notes,
        }


def load_label_map(path: Union[str, Path]) -> LabelMap:
    file_path = Path(path)
    if not file_path.is_file():
        raise AnnotationError(f"label map not found: {file_path.name}")
    payload = json.loads(file_path.read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise AnnotationError("label map must be a JSON object")

    labels = [
        LabelDefinition(
            code=str(entry.get("code", "")).strip(),
            display_name=entry.get("display_name", ""),
            source_values=tuple(entry.get("source_values") or ()),
            is_normal=bool(entry.get("is_normal", False)),
            description=entry.get("description"),
        )
        for entry in payload.get("labels", []) or []
    ]
    return LabelMap(
        schema_version=str(payload.get("schema_version", "1.0.0")),
        status=str(payload.get("status", "INPUT_REQUIRED")),
        labels=labels,
        ignore_values=tuple(payload.get("ignore_values") or ()),
        notes=payload.get("notes"),
    )


def _truthy(raw: Optional[str]) -> float:
    if raw is None:
        return 1.0
    value = str(raw).strip().lower()
    if value in ("", "0", "false", "no", "n", "absent", "negative"):
        return 0.0
    if value in ("1", "true", "yes", "y", "present", "positive"):
        return 1.0
    try:
        return float(value)
    except ValueError as exc:
        raise AnnotationError(f"unparseable label value: {value!r}") from exc


def load_annotations(path: Union[str, Path]) -> List[Dict[str, str]]:
    file_path = Path(path)
    if not file_path.is_file():
        raise AnnotationError(f"annotations not found: {file_path.name}")
    with file_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        columns = reader.fieldnames or []
        for required in ("record_id", "raw_label"):
            if required not in columns:
                raise AnnotationError(f"labels.csv missing column: {required}")
        return [dict(row) for row in reader]


def apply_label_map(
    rows: Sequence[Mapping[str, str]],
    label_map: LabelMap,
) -> Dict[str, Dict[str, float]]:
    """Return ``record_id -> {canonical_code: value}`` for all rows."""
    label_map.validate_approved()
    lookup = label_map.build_lookup()
    ignore = {str(v).strip().lower() for v in label_map.ignore_values}

    result: Dict[str, Dict[str, float]] = {}
    for row in rows:
        record_id = (row.get("record_id") or "").strip()
        raw_label = (row.get("raw_label") or "").strip()
        if not record_id or not raw_label:
            raise AnnotationError("annotation row missing record_id or raw_label")
        key = raw_label.lower()
        if key in ignore:
            continue
        if key not in lookup:
            raise AnnotationError(f"unmapped label value: {raw_label!r}")
        code = lookup[key]
        value = _truthy(row.get("value") if "value" in row else row.get("label_present"))
        result.setdefault(record_id, {})[code] = value
    return result


def attach_labels(
    records: Sequence[DatasetRecord],
    label_map: LabelMap,
    annotations: Sequence[Mapping[str, str]],
) -> None:
    """Populate ``record.labels`` in place using the approved label map."""
    mapped = apply_label_map(annotations, label_map)
    seen = set()
    for record in records:
        mapped_labels = mapped.get(record.record_id, {})
        if mapped_labels:
            record.labels.update(mapped_labels)
        seen.add(record.record_id)
    unknown = set(mapped) - seen
    if unknown:
        raise AnnotationError(
            f"annotations reference {len(unknown)} records not present in manifest"
        )
