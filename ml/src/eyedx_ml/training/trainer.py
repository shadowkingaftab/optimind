"""Training orchestration.

The :class:`Trainer` wires configs, model, optimizer, scheduler, checkpointing and
logging together. Data loaders and the loss criterion are supplied by the caller
(or built from approved artifacts); the trainer never fabricates data, labels,
metrics or thresholds.

Typical use from ``ml/scripts/train.py``::

    trainer = Trainer.from_config("ml/configs/training/baseline.yaml")
    trainer.setup()
    trainer.fit(train_loader, val_loader, criterion)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Union

from eyedx_ml.errors import NotConfiguredError
from eyedx_ml.training.checkpoint_manager import CheckpointManager, build_checkpoint_metadata
from eyedx_ml.training.early_stopping import EarlyStopping
from eyedx_ml.training.experiment_logger import ExperimentLogger
from eyedx_ml.training.optimizer_factory import build_optimizer_from_config
from eyedx_ml.training.scheduler_factory import build_scheduler_from_config
from eyedx_ml.training.seed import configure_reproducibility
from eyedx_ml.training.training_loop import train_epoch
from eyedx_ml.training.validation_loop import validate
from eyedx_ml.utils.config_loader import load_config
from eyedx_ml.utils.device import select_device
from eyedx_ml.utils.logging import get_logger

__all__ = ["Trainer"]

_logger = get_logger(__name__)


class Trainer:
    def __init__(self, config: Mapping[str, Any]):
        self.config = dict(config)
        self.model = None
        self.optimizer = None
        self.scheduler = None
        self.device_info = None
        self.early_stopping = None
        self.checkpoint_manager = None
        self.experiment_logger = None
        self.metadata: Dict[str, Any] = {}
        self.history: list = []

    # -- construction -------------------------------------------------------
    @classmethod
    def from_config(cls, path: Union[str, Path]) -> "Trainer":
        return cls(load_config(path))

    def setup(self, *, model_id: Optional[str] = None, model_version: Optional[str] = None) -> None:
        from eyedx_ml.models.model_config import load_model_config
        from eyedx_ml.models.model_factory import build_model

        repro = self.config.get("reproducibility", {}) or {}
        configure_reproducibility(
            repro.get("seed"),
            deterministic=bool(repro.get("deterministic", True)),
            benchmark=bool(repro.get("benchmark", False)),
        )

        model_cfg_path = (self.config.get("model") or {}).get("config")
        if not model_cfg_path:
            raise NotConfiguredError("training config requires model.config")
        model_config = load_model_config(model_cfg_path)
        self.model = build_model(model_config)
        self.model_config = model_config

        self.device_info = select_device("auto")
        self.model.to(self.device_info.device)

        self.optimizer = build_optimizer_from_config(
            self.model, self.config.get("optimizer", {})
        )
        epochs = int((self.config.get("training") or {}).get("epochs", 1))
        self.scheduler = build_scheduler_from_config(
            self.optimizer, self.config.get("scheduler", {}), epochs
        )

        es_cfg = ((self.config.get("training") or {}).get("early_stopping")) or {}
        self.early_stopping = EarlyStopping(
            monitor=es_cfg.get("monitor", "val_loss"),
            patience=int(es_cfg.get("patience", 0)),
            min_delta=float(es_cfg.get("min_delta", 0.0)),
            mode=es_cfg.get("mode", "min"),
        ) if es_cfg.get("enabled", False) else None

        ckpt = self.config.get("checkpointing", {}) or {}
        self.checkpoint_manager = CheckpointManager(
            ckpt.get("output_dir", "ml/checkpoints"),
            save_best=bool(ckpt.get("save_best", True)),
            save_last=bool(ckpt.get("save_last", True)),
            monitor=ckpt.get("monitor", "val_loss"),
            mode=ckpt.get("mode", "min"),
        )

        exp = self.config.get("experiment", {}) or {}
        self.experiment_logger = ExperimentLogger(
            exp.get("output_dir", "ml/experiments"),
            name=exp.get("name", self.config.get("name", "run")),
            log_every_n_steps=int(exp.get("log_every_n_steps", 50)),
        )
        self.experiment_logger.log_config(self.config)

        self.metadata = build_checkpoint_metadata(
            model_id=model_id or "INPUT_REQUIRED",
            model_version=model_version or "INPUT_REQUIRED",
            architecture=model_config.architecture,
            backbone=model_config.backbone,
            labels=list(model_config.labels),
            preprocessing=model_config.preprocessing or {},
        )

    # -- training -----------------------------------------------------------
    def fit(self, train_loader, val_loader, criterion) -> list:
        if self.model is None:
            raise NotConfiguredError("call setup() before fit()")
        train_cfg = self.config.get("training", {}) or {}
        epochs = int(train_cfg.get("epochs", 1))
        grad_accum = int(train_cfg.get("grad_accum_steps", 1))
        grad_clip = train_cfg.get("grad_clip_norm")
        device = self.device_info.device if self.device_info else "cpu"

        for epoch in range(epochs):
            train_stats = train_epoch(
                self.model,
                train_loader,
                self.optimizer,
                criterion,
                device=device,
                epoch=epoch,
                grad_accum_steps=grad_accum,
                grad_clip_norm=grad_clip,
                on_step=lambda step, loss: self.experiment_logger.log_step(
                    epoch=epoch, step=step, metrics={"loss": loss}
                ),
            )
            val_stats = validate(self.model, val_loader, criterion, device=device, epoch=epoch)
            metrics = {
                "train_loss": train_stats["loss"],
                "val_loss": val_stats["loss"],
            }

            if self.scheduler is not None:
                try:
                    self.scheduler.step(metrics["val_loss"])
                except TypeError:
                    self.scheduler.step()

            lr = self.optimizer.param_groups[0]["lr"]
            self.experiment_logger.log_epoch(epoch=epoch, metrics=metrics, lr=lr)
            saved = self.checkpoint_manager.update(
                self.model,
                self.metadata,
                epoch=epoch,
                metrics=metrics,
                optimizer=self.optimizer,
                scheduler=self.scheduler,
            )
            self.history.append({"epoch": epoch, **metrics, "checkpoints": [str(p) for p in saved]})

            if self.early_stopping is not None:
                monitor_value = metrics.get(self.early_stopping.monitor)
                if monitor_value is not None and self.early_stopping.step(monitor_value, epoch=epoch):
                    _logger.info("early stopping triggered at epoch %s", epoch)
                    break

        return self.history

    def close(self) -> None:
        if self.experiment_logger is not None:
            self.experiment_logger.close()
