"""Roll back to a previously registered model version."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional, Union

from eyedx_ml.errors import RegistryError
from eyedx_ml.registry.registry_client import FileRegistry

__all__ = ["rollback_model"]


def rollback_model(
    *,
    registry_root: Union[str, Path],
    model_id: str,
    to_version: Optional[str] = None,
    approved_by: Optional[str] = None,
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    """Restore a prior version to production.

    When ``to_version`` is omitted, the most recent non-production, non-archived
    version is selected. Rollback to production requires ``approved_by``.
    """
    registry = FileRegistry(registry_root)
    if to_version is None:
        candidates = [
            v for v in registry.list_versions(model_id) if v.get("stage") not in ("production", "archived")
        ]
        if not candidates:
            raise RegistryError(f"no rollback candidate found for {model_id}")
        to_version = candidates[-1]["model_version"]

    return registry.set_stage(
        model_id=model_id,
        model_version=to_version,
        stage="production",
        approved_by=approved_by,
        notes=notes or f"rollback to {to_version}",
    )
