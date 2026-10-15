"""Build models from :class:`ModelConfig`.

Heavy imports (torch) happen only inside the builder functions. When required
inputs (labels, weights) are absent, builders raise the relevant
:class:`eyedx_ml.errors` exception rather than fabricating values.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional, Union

from eyedx_ml.errors import NotConfiguredError
from eyedx_ml.models.model_config import ModelConfig, load_model_config

__all__ = ["build_model", "build_model_from_file", "describe_model"]


def _resolve_num_labels(config: ModelConfig) -> int:
    return config.resolved_num_labels()


def build_model(config: ModelConfig):
    """Instantiate an nn.Module described by ``config``."""
    config.validate()
    arch = config.architecture
    backbone = config.backbone
    common: Dict[str, Any] = dict(
        pretrained=config.pretrained,
        weights_path=config.pretrained_weights_path(),
        in_channels=config.in_channels,
        dropout=config.dropout,
    )

    if arch == "binary_classifier":
        from eyedx_ml.models.classifiers import BinaryClassifier

        return BinaryClassifier(
            backbone, hidden_dim=config.hidden_dim or None, **common
        )

    if arch == "multiclass_classifier":
        from eyedx_ml.models.classifiers import MulticlassClassifier

        num_labels = _resolve_num_labels(config)
        return MulticlassClassifier(
            backbone,
            num_classes=num_labels,
            hidden_dim=config.hidden_dim or None,
            **common,
        )

    if arch == "multilabel_classifier":
        from eyedx_ml.models.classifiers import MultiLabelClassifier

        num_labels = _resolve_num_labels(config)
        return MultiLabelClassifier(
            backbone,
            num_labels=num_labels,
            labels=config.load_approved_labels() if config.labels else None,
            hidden_dim=config.hidden_dim or None,
            **common,
        )

    if arch == "multitask":
        from eyedx_ml.models.multitask import MultiTaskModel

        multitask = config.multitask or {}
        heads = multitask.get("heads") or multitask.get("tasks") or {}
        return MultiTaskModel(
            backbone,
            heads if isinstance(heads, dict) else {},
            hidden_dim=config.hidden_dim or None,
            **common,
        )

    if arch == "segmentation":
        from eyedx_ml.models.segmentation import build_unet

        seg = config.segmentation or {}
        return build_unet(
            config.in_channels,
            int(seg.get("num_classes", 0)),
            base_channels=int(seg.get("base_channels", 64)),
            depth=int(seg.get("depth", 4)),
        )

    if arch == "ensemble":
        raise NotConfiguredError(
            "ensemble models are assembled from member checkpoints at inference "
            "time via eyedx_ml.models.ensembles; provide member checkpoints and "
            "weights (INPUT_REQUIRED)"
        )

    raise NotConfiguredError(f"unsupported architecture: {arch}")


def build_model_from_file(path: Union[str, Path]):
    return build_model(load_model_config(path))


def describe_model(module, *, config: Optional[ModelConfig] = None) -> Dict[str, Any]:
    """Return a JSON-serialisable summary of a built model."""
    info: Dict[str, Any] = {"class": type(module).__name__}
    try:
        total = sum(p.numel() for p in module.parameters())
        trainable = sum(p.numel() for p in module.parameters() if p.requires_grad)
        info["parameters"] = total
        info["trainable_parameters"] = trainable
    except Exception:  # pragma: no cover - non-torch module
        pass
    if config is not None:
        info["config"] = config.to_dict()
    return info
