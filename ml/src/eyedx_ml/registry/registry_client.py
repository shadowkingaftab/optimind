"""File-based ML model registry.

Stores model packages and stage metadata on the local filesystem. This is the
ML-side registry used for reproducibility; promotion to production must still go
through approval. No model is ever marked production automatically.
"""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Union

from eyedx_ml.errors import RegistryError

__all__ = ["FileRegistry", "STAGES"]

STAGES = ("development", "staging", "production", "archived")


class FileRegistry:
    def __init__(self, root: Union[str, Path]) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.index_path = self.root / "index.json"

    # -- index --------------------------------------------------------------
    def _read_index(self) -> Dict[str, Any]:
        if not self.index_path.is_file():
            return {"models": {}}
        return json.loads(self.index_path.read_text(encoding="utf-8"))

    def _write_index(self, index: Mapping[str, Any]) -> None:
        self.index_path.write_text(json.dumps(index, indent=2), encoding="utf-8")

    # -- registration -------------------------------------------------------
    def register(
        self,
        *,
        model_id: str,
        model_version: str,
        package_dir: Union[str, Path],
        stage: str = "development",
        metadata: Optional[Mapping[str, Any]] = None,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        if stage not in STAGES:
            raise RegistryError(f"invalid stage: {stage}")
        package_dir = Path(package_dir)
        if not package_dir.is_dir():
            raise RegistryError(f"package directory not found: {package_dir.name}")

        dest = self.root / model_id / model_version
        if dest.exists():
            raise RegistryError(
                f"model {model_id}@{model_version} already registered"
            )
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(package_dir, dest)

        entry = {
            "model_id": model_id,
            "model_version": model_version,
            "stage": stage,
            "registered_at": datetime.now(timezone.utc).isoformat(),
            "path": str(dest),
            "notes": notes,
            "metadata": dict(metadata or {}),
            "history": [{"stage": stage, "at": datetime.now(timezone.utc).isoformat()}],
        }
        index = self._read_index()
        index["models"].setdefault(model_id, {})[model_version] = entry
        self._write_index(index)
        return entry

    # -- queries ------------------------------------------------------------
    def list_versions(self, model_id: str) -> List[Dict[str, Any]]:
        return list(self._read_index()["models"].get(model_id, {}).values())

    def get(self, model_id: str, model_version: str) -> Optional[Dict[str, Any]]:
        return self._read_index()["models"].get(model_id, {}).get(model_version)

    def current_stage(self, model_id: str, stage: str) -> Optional[str]:
        versions = [
            v["model_version"]
            for v in self.list_versions(model_id)
            if v.get("stage") == stage
        ]
        return versions[-1] if versions else None

    # -- lifecycle ----------------------------------------------------------
    def set_stage(
        self,
        *,
        model_id: str,
        model_version: str,
        stage: str,
        approved_by: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        if stage not in STAGES:
            raise RegistryError(f"invalid stage: {stage}")
        if stage == "production" and not approved_by:
            raise RegistryError(
                "promotion to production requires approved_by (INPUT_REQUIRED: "
                "named approver)"
            )
        index = self._read_index()
        entry = index["models"].get(model_id, {}).get(model_version)
        if entry is None:
            raise RegistryError(f"model not found: {model_id}@{model_version}")
        entry["stage"] = stage
        entry["history"].append(
            {
                "stage": stage,
                "at": datetime.now(timezone.utc).isoformat(),
                "approved_by": approved_by,
                "notes": notes,
            }
        )
        self._write_index(index)
        return entry

    def archive(self, *, model_id: str, model_version: str, notes: Optional[str] = None) -> Dict[str, Any]:
        return self.set_stage(
            model_id=model_id, model_version=model_version, stage="archived", notes=notes
        )
