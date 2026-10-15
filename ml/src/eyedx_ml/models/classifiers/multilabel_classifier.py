"""Multi-label screening classifier."""

from __future__ import annotations

from typing import Optional, Sequence

from eyedx_ml.errors import DependencyError, NotConfiguredError

__all__ = ["MultiLabelClassifier"]


def _torch():
    try:
        import torch
    except Exception as exc:  # pragma: no cover - optional dependency
        raise DependencyError("torch is required to build classifiers") from exc
    return torch


class MultiLabelClassifier:
    """Backbone + pooling + independent logits per approved label."""

    def __new__(
        cls,
        backbone: str,
        *,
        num_labels: int,
        labels: Optional[Sequence[str]] = None,
        pretrained: bool = False,
        weights_path: Optional[str] = None,
        in_channels: int = 3,
        dropout: float = 0.0,
        hidden_dim: Optional[int] = None,
    ):
        torch = _torch()
        from eyedx_ml.models.backbones import create_backbone
        from eyedx_ml.models.layers import classification_head, global_pool

        if not backbone:
            raise NotConfiguredError("MultiLabelClassifier requires a backbone")
        if not num_labels or num_labels < 1:
            raise NotConfiguredError(
                "num_labels is INPUT_REQUIRED: supply approved labels before "
                "building a multi-label model"
            )

        class _MultiLabelClassifier(torch.nn.Module):
            def __init__(self) -> None:
                super().__init__()
                self.backbone = create_backbone(
                    backbone,
                    pretrained=pretrained,
                    weights_path=weights_path,
                    in_channels=in_channels,
                )
                self.pool = global_pool("avg")
                self.head = classification_head(
                    self.backbone.out_channels,
                    num_labels,
                    hidden_dim=hidden_dim,
                    dropout=dropout,
                    activation="none",
                )
                self.num_labels = num_labels
                self.labels = list(labels or [])

            def forward(self, x):
                features = self.backbone(x)
                pooled = self.pool(features).flatten(1)
                return self.head(pooled)

            def predict_proba(self, x):
                return torch.sigmoid(self.forward(x))

        return _MultiLabelClassifier()
