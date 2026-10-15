"""Model packaging: bundle weights, metadata and a manifest for handoff."""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Union

from eyedx_ml.errors import ExportError
from eyedx_ml.export.export_metadata import validate_metadata

__all__ = ["package_model", "MANIFEST_NAME"]

MANIFEST_NAME = "package-manifest.json"


def package_model(
    output_dir: Union[str, Path],
    *,
    metadata: Mapping[str, Any],
    artifacts: Mapping[str, Union[str, Path]],
    readme: Optional[str] = None,
    overwrite: bool = False,
) -> Dict[str, Any]:
    """Assemble a model package directory.

    ``artifacts`` maps a logical name (e.g. ``"model"``, ``"onnx"``) to an
    existing file path. Metadata is validated against the model-metadata
    contract before packaging.
    """
    problems = validate_metadata(metadata)
    if problems:
        raise ExportError("invalid model metadata: " + "; ".join(problems))
    if not artifacts:
        raise ExportError("at least one artifact is required")

    output_dir = Path(output_dir)
    if output_dir.exists() and not overwrite:
        raise ExportError(f"output directory already exists: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)

    copied: Dict[str, str] = {}
    for name, src in artifacts.items():
        src = Path(src)
        if not src.is_file():
            raise ExportError(f"artifact not found for {name!r}: {src.name}")
        dst = output_dir / src.name
        shutil.copy2(src, dst)
        copied[name] = dst.name

    meta_path = output_dir / "model-metadata.json"
    meta_path.write_text(json.dumps(dict(metadata), indent=2), encoding="utf-8")

    if readme:
        (output_dir / "README.md").write_text(readme, encoding="utf-8")

    manifest = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "model_id": metadata.get("model_id"),
        "model_version": metadata.get("model_version"),
        "artifacts": copied,
        "metadata_file": meta_path.name,
    }
    (output_dir / MANIFEST_NAME).write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    return manifest
