"""Binary screening classifier (single logit)."""

from __future__ import annotations

from typing import Optional

from eyedx_ml.errors import DependencyError, NotConfiguredError

__all__ = ["BinaryClassifier"]


def _torch():
    try:
        import torch
    except Exception as exc:  # pragma: no cover - optional dependency
        raise DependencyError("torch is required to build classifiers") from exc
    return torch


class BinaryClassifier:
    """Backbone + pooling + single-logit head.

    ``forward`` returns logits of shape (B, 1). This class is a factory wrapper;
    instantiate via :func:`eyedx_ml.models.model_factory.build_model`.
    """

    def __new__(
        cls,
        backbone: str,
        *,
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
            raise NotConfiguredError("BinaryClassifier requires a backbone")

        class _BinaryClassifier(torch.nn.Module):
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
                    1,
                    hidden_dim=hidden_dim,
                    dropout=dropout,
                    activation="none",
                )
                self.num_labels = 1

            def forward(self, x):
                features = self.backbone(x)
                pooled = self.pool(features).flatten(1)
                return self.head(pooled)

            def predict_proba(self, x):
                return torch.sigmoid(self.forward(x))

        return _BinaryClassifier()
