"""Multi-task model: shared backbone with disease/quality/severity heads."""

from __future__ import annotations

from typing import Any, Dict, Mapping, Optional

from eyedx_ml.errors import DependencyError, NotConfiguredError

__all__ = ["MultiTaskModel"]


def _torch():
    try:
        import torch
    except Exception as exc:  # pragma: no cover - optional dependency
        raise DependencyError("torch is required for MultiTaskModel") from exc
    return torch


class MultiTaskModel:
    """Factory returning an nn.Module with a shared backbone and multiple heads.

    ``tasks`` maps a task name to its head spec. Heads may be given as a plain
    task mapping or in the config style with a ``type``::

        {"disease": {"type": "multilabel", "labels": [...]},
         "quality": {"type": "multiclass", "classes": ["good", "usable", "unusable"]},
         "severity": {"type": "ordinal", "enabled": false, "levels": []}}

    ``forward`` returns ``{task_name: logits}``. Labels/levels are INPUT_REQUIRED
    and must come from the approved label map and annotation schema.
    """

    def __new__(
        cls,
        backbone: str,
        tasks: Mapping[str, Mapping[str, Any]],
        *,
        pretrained: bool = False,
        weights_path: Optional[str] = None,
        in_channels: int = 3,
        dropout: float = 0.0,
        hidden_dim: Optional[int] = None,
    ):
        torch = _torch()
        from eyedx_ml.models.backbones import create_backbone
        from eyedx_ml.models.layers import global_pool
        from eyedx_ml.models.multitask.disease_head import build_disease_head
        from eyedx_ml.models.multitask.quality_head import build_quality_head
        from eyedx_ml.models.multitask.severity_head import build_severity_head

        if not tasks:
            raise NotConfiguredError("MultiTaskModel requires at least one task")

        class _MultiTaskModel(torch.nn.Module):
            def __init__(self) -> None:
                super().__init__()
                self.backbone = create_backbone(
                    backbone,
                    pretrained=pretrained,
                    weights_path=weights_path,
                    in_channels=in_channels,
                )
                self.pool = global_pool("avg")
                in_features = self.backbone.out_channels
                self.heads = torch.nn.ModuleDict()
                for name, raw_spec in tasks.items():
                    spec = dict(raw_spec or {})
                    if name == "severity" and spec.get("enabled", True) is False:
                        continue
                    if name in ("disease", "multilabel"):
                        labels = spec.get("labels") or []
                        num = len(labels) or int(
                            spec.get("num_labels") or spec.get("num_outputs") or 0
                        )
                        self.heads[name] = build_disease_head(
                            in_features,
                            num,
                            hidden_dim=hub_hidden(spec, hidden_dim),
                            dropout=float(spec.get("dropout", dropout)),
                        )
                    elif name == "quality":
                        classes = spec.get("classes") or []
                        num = len(classes) or int(spec.get("num_outputs", 1))
                        self.heads[name] = build_quality_head(
                            in_features,
                            num_outputs=num,
                            regression=bool(spec.get("regression", False)),
                            hidden_dim=hub_hidden(spec, hidden_dim),
                            dropout=float(spec.get("dropout", dropout)),
                        )
                    elif name == "severity":
                        levels = spec.get("levels") or []
                        num = len(levels) or int(spec.get("num_levels", 0))
                        self.heads[name] = build_severity_head(
                            in_features,
                            num,
                            hidden_dim=hub_hidden(spec, hidden_dim),
                            dropout=float(spec.get("dropout", dropout)),
                        )
                    else:
                        raise NotConfiguredError(f"unknown task: {name}")

            def forward(self, x) -> Dict[str, object]:
                features = self.backbone(x)
                pooled = self.pool(features).flatten(1)
                return {name: head(pooled) for name, head in self.heads.items()}

        return _MultiTaskModel()


def hub_hidden(spec: Mapping[str, Any], default: Optional[int]) -> Optional[int]:
    value = spec.get("hidden_dim", default)
    return int(value) if value else None
