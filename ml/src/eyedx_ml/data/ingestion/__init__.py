"""Data ingestion: sources, manifests, metadata and annotations."""

from __future__ import annotations

from .annotation_importer import (
    AnnotationError,
    LabelDefinition,
    LabelMap,
    apply_label_map,
    attach_labels,
    load_annotations,
    load_label_map,
)
from .dataset_importer import (
    MANIFEST_COLUMNS,
    DatasetError,
    DatasetRecord,
    pseudonymize,
    read_manifest,
    write_manifest,
)
from .metadata_importer import (
    REQUIRED_COLUMNS,
    MetadataError,
    MetadataTable,
    load_metadata_table,
    load_metadata_tables,
)
from .source_registry import (
    DataSource,
    SourceError,
    SourceRegistry,
    load_source_registry,
)

__all__ = [
    "AnnotationError",
    "LabelDefinition",
    "LabelMap",
    "apply_label_map",
    "attach_labels",
    "load_annotations",
    "load_label_map",
    "MANIFEST_COLUMNS",
    "DatasetError",
    "DatasetRecord",
    "pseudonymize",
    "read_manifest",
    "write_manifest",
    "REQUIRED_COLUMNS",
    "MetadataError",
    "MetadataTable",
    "load_metadata_table",
    "load_metadata_tables",
    "DataSource",
    "SourceError",
    "SourceRegistry",
    "load_source_registry",
]
