"""Batched inference."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from eyedx_ml.errors import DependencyError, NotConfiguredError

__all__ = ["BatchPredictor"]


class BatchPredictor:
    """Runs a torch model over an iterable of input tensors in batches."""

    def __init__(self, model, *, batch_size: int = 8, device: str = "cpu") -> None:
        if batch_size < 1:
            raise NotConfiguredError("batch_size must be >= 1")
        self.model = model
        self.model.eval()
        self.batch_size = int(batch_size)
        self.device = device

    def predict_proba(self, batches: Iterable) -> List[Any]:
        try:
            import torch
        except Exception as exc:  # pragma: no cover - optional dependency
            raise DependencyError("torch is required for batch prediction") from exc

        outputs: List[Any] = []
        with torch.no_grad():
            for batch in batches:
                tensor = batch.to(self.device)
                logits = self.model(tensor)
                if isinstance(logits, dict):
                    raise NotConfiguredError("BatchPredictor expects a single-output model")
                outputs.append(torch.sigmoid(logits).detach().cpu())
        return outputs

    def predict_batch(self, tensor) -> Any:
        try:
            import torch
        except Exception as exc:  # pragma: no cover - optional dependency
            raise DependencyError("torch is required for batch prediction") from exc
        with torch.no_grad():
            logits = self.model(tensor.to(self.device))
            if isinstance(logits, dict):
                raise NotConfiguredError("BatchPredictor expects a single-output model")
            return torch.sigmoid(logits).detach().cpu()
