"""Early stopping."""

from __future__ import annotations

from typing import Optional

__all__ = ["EarlyStopping"]


class EarlyStopping:
    """Track a monitored metric and signal when training should stop.

    ``mode`` is ``min`` or ``max``. ``min_delta`` is the minimum improvement to
    count as progress. The monitored metric must be computed from the validation
    split, never the test split.
    """

    def __init__(
        self,
        *,
        monitor: str = "val_loss",
        patience: int = 5,
        min_delta: float = 0.0,
        mode: str = "min",
    ) -> None:
        if mode not in ("min", "max"):
            raise ValueError("mode must be 'min' or 'max'")
        self.monitor = monitor
        self.patience = int(patience)
        self.min_delta = float(min_delta)
        self.mode = mode
        self.best: Optional[float] = None
        self.best_epoch: Optional[int] = None
        self.num_bad_epochs = 0

    def _improved(self, value: float) -> bool:
        if self.best is None:
            return True
        if self.mode == "min":
            return value < (self.best - self.min_delta)
        return value > (self.best + self.min_delta)

    def step(self, value: float, *, epoch: Optional[int] = None) -> bool:
        """Update state. Returns ``True`` when training should stop."""
        if value is None:
            return False
        if self._improved(float(value)):
            self.best = float(value)
            self.best_epoch = epoch
            self.num_bad_epochs = 0
        else:
            self.num_bad_epochs += 1
        return self.num_bad_epochs >= self.patience if self.patience > 0 else False

    @property
    def should_stop(self) -> bool:
        return self.patience > 0 and self.num_bad_epochs >= self.patience

    def state_dict(self) -> dict:
        return {
            "monitor": self.monitor,
            "best": self.best,
            "best_epoch": self.best_epoch,
            "num_bad_epochs": self.num_bad_epochs,
        }
