"""Validate an exported/packaged model directory."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Union

from eyedx_ml.errors import ExportError
from eyedx_ml.export.package_model import MANIFEST_NAME
from eyedx_ml.export.export_metadata import validate_metadata

__all__ = ["validate_export"]


def validate_export(path: Union[str, Path]) -> Dict[str, Any]:
    """Check a package directory for required files and valid metadata."""
    path = Path(path)
    if not path.is_dir():
        raise ExportError(f"package directory not found: {path}")

    problems: List[str] = []
    manifest_path = path / MANIFEST_NAME
    metadata_path = path / "model-metadata.json"

    if not manifest_path.is_file():
        problems.append(f"missing {MANIFEST_NAME}")
    if not metadata_path.is_file():
        problems.append("missing model-metadata.json")

    metadata: Dict[str, Any] = {}
    if metadata_path.is_file():
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        problems.extend(validate_metadata(metadata))

    artifacts: Dict[str, str] = {}
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        artifacts = manifest.get("artifacts", {})
        for name, filename in artifacts.items():
            if not (path / filename).is_file():
                problems.append(f"manifest artifact missing on disk: {name} -> {filename}")

    return {
        "path": str(path),
        "valid": not problems,
        "problems": problems,
        "metadata": metadata,
        "artifacts": artifacts,
    }
