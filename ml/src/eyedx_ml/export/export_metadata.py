"""Model metadata export (aligned to the model-metadata contract)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Mapping, Union

from eyedx_ml.errors import ExportError

__all__ = ["validate_metadata", "write_model_metadata", "read_model_metadata"]

REQUIRED_FIELDS = ("model_id", "model_version", "created_at", "labels", "preprocessing", "capabilities")
REQUIRED_CAPABILITIES = ("supports_uncertainty", "supports_explanation", "supports_abstention")


def validate_metadata(metadata: Mapping[str, Any]) -> List[str]:
    """Return a list of contract violations (empty when valid)."""
    problems: List[str] = []
    for field in REQUIRED_FIELDS:
        if field not in metadata or metadata[field] in (None, ""):
            problems.append(f"missing required field: {field}")
    caps = metadata.get("capabilities")
    if isinstance(caps, dict):
        for key in REQUIRED_CAPABILITIES:
            if key not in caps:
                problems.append(f"capabilities missing {key}")
            elif not isinstance(caps[key], bool):
                problems.append(f"capabilities.{key} must be boolean")
    elif caps is not None:
        problems.append("capabilities must be an object")
    if not metadata.get("labels"):
        problems.append("labels must be a non-empty vocabulary")
    return problems


def write_model_metadata(
    metadata: Mapping[str, Any], path: Union[str, Path]
) -> str:
    problems = validate_metadata(metadata)
    if problems:
        raise ExportError("invalid model metadata: " + "; ".join(problems))
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(metadata), indent=2), encoding="utf-8")
    return str(path)


def read_model_metadata(path: Union[str, Path]) -> Dict[str, Any]:
    path = Path(path)
    if not path.is_file():
        raise ExportError(f"metadata file not found: {path.name}")
    return json.loads(path.read_text(encoding="utf-8"))
