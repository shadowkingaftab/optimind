"""Promote a registered model between stages."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional, Union

from eyedx_ml.registry.registry_client import FileRegistry

__all__ = ["promote_model"]


def promote_model(
    *,
    registry_root: Union[str, Path],
    model_id: str,
    model_version: str,
    stage: str = "staging",
    approved_by: Optional[str] = None,
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    """Move a model to a stage.

    Promotion to ``production`` requires ``approved_by`` (INPUT_REQUIRED: named
    approver) — approval is never bypassed.
    """
    registry = FileRegistry(registry_root)
    return registry.set_stage(
        model_id=model_id,
        model_version=model_version,
        stage=stage,
        approved_by=approved_by,
        notes=notes,
    )
