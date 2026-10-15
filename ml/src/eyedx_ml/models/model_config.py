"""Model configuration and label binding.

Loads a model config (YAML/dict), validates it, and binds the approved label
vocabulary. Labels are never invented: when a config references
``require_approved_label_map`` and the map is missing or unapproved, the config
still loads (so shape can be inspected) but resolving labels raises
:class:`LabelUnavailableError`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Union

from eyedx_ml.errors import LabelUnavailableError, NotConfiguredError
from eyedx_ml.utils.config_loader import load_config

__all__ = [
    "ARCHITECTURES",
    "ModelConfigError",
    "ModelConfig",
    "load_model_config",
]

ARCHITECTURES = (
    "binary_classifier",
    "multiclass_classifier",
    "multilabel_classifier",
    "multitask",
    "segmentation",
    "ensemble",
)

_MISSING = "INPUT_REQUIRED"


class ModelConfigError(ValueError):
    """Raised for malformed model configuration."""


def _is_missing(value: Any) -> bool:
    return value is None or (isinstance(value, str) and _MISSING in value)


@dataclass
class ModelConfig:
    name: str
    architecture: str
    backbone: Optional[str] = None
    pretrained: bool = False
    pretrained_weights: Optional[str] = None
    in_channels: int = 3
    input_size: Sequence[int] = (512, 512)
    dropout: float = 0.2
    hidden_dim: int = 512
    labels: List[str] = field(default_factory=list)
    num_labels: Optional[int] = None
    label_map: Optional[str] = None
    require_approved_label_map: bool = True
    preprocessing: Dict[str, Any] = field(default_factory=dict)
    segmentation: Optional[Dict[str, Any]] = None
    multitask: Optional[Dict[str, Any]] = None
    ensemble: Optional[Dict[str, Any]] = None
    loss: Dict[str, Any] = field(default_factory=dict)
    schema_version: str = "1.0.0"
    description: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    # -- validation ---------------------------------------------------------
    def validate(self) -> None:
        if self.architecture not in ARCHITECTURES:
            raise ModelConfigError(
                f"unknown architecture {self.architecture!r}; "
                f"expected one of {', '.join(ARCHITECTURES)}"
            )
        if not self.pretrained_weights and self.pretrained:
            raise ModelConfigError(
                "pretrained=True requires pretrained_weights (INPUT_REQUIRED)"
            )
        if len(self.input_size) != 2 or any(int(v) <= 0 for v in self.input_size):
            raise ModelConfigError("input_size must be [width, height] positives")
        if self.num_labels is not None and self.num_labels <= 0:
            raise ModelConfigError("num_labels must be positive when set")
        if (
            self.num_labels is not None
            and self.labels
            and self.num_labels != len(self.labels)
        ):
            raise ModelConfigError(
                "num_labels must equal len(labels) when both are provided"
            )

    # -- capability queries -------------------------------------------------
    @property
    def labels_available(self) -> bool:
        return bool(self.labels) and not _is_missing(self.num_labels)

    def resolved_num_labels(self) -> int:
        """Return the label count or raise when labels are not yet available."""
        if self.labels:
            return len(self.labels)
        if self.num_labels and not _is_missing(self.num_labels):
            return int(self.num_labels)
        raise LabelUnavailableError(
            "no approved labels configured; supply the approved label map and "
            "populate `labels`/`num_labels` before building a model"
        )

    def load_approved_labels(self) -> List[str]:
        """Return canonical label codes from the approved label map."""
        if self.labels:
            return list(self.labels)
        if not self.label_map:
            raise LabelUnavailableError("no label_map configured")
        path = Path(self.label_map)
        if not path.is_file():
            raise LabelUnavailableError(f"label map not found: {path.name}")
        from eyedx_ml.data.ingestion.annotation_importer import (
            AnnotationError,
            load_label_map,
        )

        label_map = load_label_map(path)
        try:
            label_map.validate_approved()
        except AnnotationError as exc:
            raise LabelUnavailableError(str(exc)) from exc
        return label_map.codes()

    def pretrained_weights_path(self) -> Optional[str]:
        """Return a concrete weights path/identifier, or ``None`` when absent."""
        if self.pretrained_weights and not _is_missing(self.pretrained_weights):
            return self.pretrained_weights
        return None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "name": self.name,
            "architecture": self.architecture,
            "backbone": self.backbone,
            "pretrained": self.pretrained,
            "pretrained_weights": self.pretrained_weights,
            "in_channels": self.in_channels,
            "input_size": list(self.input_size),
            "dropout": self.dropout,
            "hidden_dim": self.hidden_dim,
            "labels": list(self.labels),
            "num_labels": self.num_labels,
            "label_map": self.label_map,
            "require_approved_label_map": self.require_approved_label_map,
            "preprocessing": dict(self.preprocessing),
            "segmentation": self.segmentation,
            "multitask": self.multitask,
            "ensemble": self.ensemble,
            "loss": dict(self.loss),
            "description": self.description,
        }

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "ModelConfig":
        if "architecture" not in data:
            raise ModelConfigError("model config requires an 'architecture'")
        known = {
            "schema_version",
            "name",
            "architecture",
            "backbone",
            "pretrained",
            "pretrained_weights",
            "in_channels",
            "input_size",
            "dropout",
            "hidden_dim",
            "labels",
            "num_labels",
            "label_map",
            "require_approved_label_map",
            "preprocessing",
            "segmentation",
            "multitask",
            "ensemble",
            "loss",
            "description",
        }
        extra = {k: v for k, v in data.items() if k not in known}
        config = cls(
            name=str(data.get("name") or "model"),
            architecture=str(data["architecture"]),
            backbone=data.get("backbone"),
            pretrained=bool(data.get("pretrained", False)),
            pretrained_weights=data.get("pretrained_weights"),
            in_channels=int(data.get("in_channels", 3)),
            input_size=tuple(data.get("input_size") or (512, 512)),
            dropout=float(data.get("dropout", 0.2)),
            hidden_dim=int(data.get("hidden_dim", 512)),
            labels=list(data.get("labels") or []),
            num_labels=data.get("num_labels"),
            label_map=data.get("label_map"),
            require_approved_label_map=bool(
                data.get("require_approved_label_map", True)
            ),
            preprocessing=dict(data.get("preprocessing") or {}),
            segmentation=data.get("segmentation"),
            multitask=data.get("multitask"),
            ensemble=data.get("ensemble"),
            loss=dict(data.get("loss") or {}),
            schema_version=str(data.get("schema_version", "1.0.0")),
            description=data.get("description"),
            extra=extra,
        )
        config.validate()
        return config


def load_model_config(path: Union[str, Path]) -> ModelConfig:
    """Load and validate a model config from a YAML file."""
    try:
        data = load_config(path)
    except NotConfiguredError:
        raise
    except Exception as exc:
        raise ModelConfigError(f"could not load model config: {exc}") from exc
    return ModelConfig.from_mapping(data)
