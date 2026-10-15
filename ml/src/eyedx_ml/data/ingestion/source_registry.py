"""Data source registry.

Sources are declared in configuration (never hard-coded) and must carry licence
and consent provenance. The registry refuses to register a source missing
required provenance fields, so unlicensed data cannot silently enter a run.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Union

__all__ = ["SourceError", "DataSource", "SourceRegistry", "load_source_registry"]

_REQUIRED_FIELDS = ("name", "root_path", "license_name")


class SourceError(ValueError):
    """Raised when a data source is missing required provenance."""


@dataclass(frozen=True)
class DataSource:
    name: str
    root_path: str
    license_name: str
    kind: str = "fundus"
    license_url: Optional[str] = None
    citation: Optional[str] = None
    consent_status: Optional[str] = None
    manifest_path: Optional[str] = None
    image_root: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        for field_name in _REQUIRED_FIELDS:
            value = getattr(self, field_name)
            if not value or not str(value).strip():
                raise SourceError(
                    f"source is missing required provenance field: {field_name}"
                )
        if "INPUT_REQUIRED" in str(self.license_name):
            raise SourceError("source license is not approved (INPUT_REQUIRED)")

    @property
    def image_root_path(self) -> Path:
        base = Path(self.image_root or self.root_path)
        return base

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "kind": self.kind,
            "root_path": self.root_path,
            "image_root": self.image_root,
            "manifest_path": self.manifest_path,
            "license_name": self.license_name,
            "license_url": self.license_url,
            "citation": self.citation,
            "consent_status": self.consent_status,
            "metadata": dict(self.metadata),
        }


class SourceRegistry:
    """An immutable collection of validated sources."""

    def __init__(self, sources: List[DataSource]) -> None:
        for source in sources:
            source.validate()
        self._sources: Dict[str, DataSource] = {s.name: s for s in sources}

    def __iter__(self):
        return iter(self._sources.values())

    def __len__(self) -> int:
        return len(self._sources)

    def get(self, name: str) -> DataSource:
        if name not in self._sources:
            raise SourceError(f"unknown data source: {name}")
        return self._sources[name]

    def names(self) -> List[str]:
        return sorted(self._sources.keys())


def load_source_registry(config: Union[str, Path, Mapping[str, Any]]) -> SourceRegistry:
    """Build a registry from a config path or mapping.

    Expected shape::

        sources:
          - name: my-dataset
            root_path: /data/my-dataset
            license_name: CC-BY-4.0
            ...
    """
    if isinstance(config, (str, Path)):
        from eyedx_ml.utils.config_loader import load_config

        data = load_config(config)
    else:
        data = dict(config)

    raw_sources = data.get("sources")
    if not isinstance(raw_sources, list) or not raw_sources:
        raise SourceError("no sources configured; licensed data is required")

    sources: List[DataSource] = []
    for entry in raw_sources:
        if not isinstance(entry, Mapping):
            raise SourceError("each source must be a mapping")
        unknown = set(entry) - set(DataSource.__dataclass_fields__)  # type: ignore[attr-defined]
        if unknown:
            raise SourceError(f"unknown source fields: {sorted(unknown)}")
        sources.append(DataSource(**dict(entry)))
    return SourceRegistry(sources)
