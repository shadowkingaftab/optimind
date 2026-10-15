"""Register a packaged model into the file registry."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Union

from eyedx_ml.errors import RegistryError
from eyedx_ml.export.validate_export import validate_export
from eyedx_ml.registry.registry_client import FileRegistry

__all__ = ["register_model"]


def register_model(
    package_dir: Union[str, Path],
    *,
    registry_root: Union[str, Path],
    stage: str = "development",
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    """Validate a model package then register it.

    The package must contain valid model metadata (see
    :func:`eyedx_ml.export.validate_export`).
    """
    validation = validate_export(package_dir)
    if not validation["valid"]:
        raise RegistryError(
            "cannot register invalid package: " + "; ".join(validation["problems"])
        )
    metadata: Mapping[str, Any] = validation["metadata"]
    registry = FileRegistry(registry_root)
    return registry.register(
        model_id=metadata["model_id"],
        model_version=metadata["model_version"],
        package_dir=package_dir,
        stage=stage,
        metadata=metadata,
        notes=notes,
    )
