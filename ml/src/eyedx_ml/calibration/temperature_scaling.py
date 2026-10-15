"""Temperature scaling for probability calibration."""

from __future__ import annotations

from typing import Any, Dict

from eyedx_ml.errors import DependencyError, NotConfiguredError

__all__ = ["TemperatureScaler", "apply_temperature"]


def _torch():
    try:
        import torch
    except Exception as exc:  # pragma: no cover - optional dependency
        raise DependencyError("torch is required for temperature scaling") from exc
    return torch


def apply_temperature(logits, temperature: float):
    """Divide logits by a positive temperature (binary or multi-class)."""
    if temperature <= 0:
        raise NotConfiguredError("temperature must be positive")
    return logits / float(temperature)


class TemperatureScaler:
    """Fit a single temperature on validation logits to minimise NLL.

    ``binary`` selects BCE; otherwise cross-entropy is used. Fit only on the
    validation split to avoid leakage.
    """

    def __new__(cls):
        torch = _torch()

        class _TemperatureScaler(torch.nn.Module):
            def __init__(self) -> None:
                super().__init__()
                self.temperature = torch.nn.Parameter(torch.ones(1))
                self._fitted = False
                self.binary = False

            def forward(self, logits):
                return logits / self.temperature.clamp_min(1e-3)

            def fit(
                self,
                logits,
                targets,
                *,
                binary: bool = False,
                lr: float = 0.01,
                max_iter: int = 50,
            ):
                self.binary = binary
                logits = torch.as_tensor(logits, dtype=torch.float32)
                targets = torch.as_tensor(targets, dtype=torch.float32)
                optimizer = torch.optim.LBFGS([self.temperature], lr=lr, max_iter=max_iter)

                def closure():
                    optimizer.zero_grad()
                    scaled = self.forward(logits)
                    if binary:
                        loss = torch.nn.functional.binary_cross_entropy_with_logits(
                            scaled, targets
                        )
                    else:
                        loss = torch.nn.functional.cross_entropy(
                            scaled, targets.long()
                        )
                    loss.backward()
                    return loss

                optimizer.step(closure)
                self._fitted = True
                return float(self.temperature.detach().item())

            @property
            def fitted(self) -> bool:
                return self._fitted

            def state_dict(self) -> Dict[str, Any]:  # type: ignore[override]
                return {"temperature": float(self.temperature.detach().item())}

        return _TemperatureScaler()
