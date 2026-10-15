"""Single-image predictor.

Loads an approved checkpoint + label vocabulary and produces contract-aligned
responses. Missing artifacts or labels raise the relevant error rather than
returning fabricated output.
"""

from __future__ import annotations

import time
import uuid
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Sequence, Union

from eyedx_ml.errors import ArtifactUnavailableError, LabelUnavailableError, NotConfiguredError
from eyedx_ml.inference.prediction_formatter import format_predictions, format_response
from eyedx_ml.inference.quality_gate import QualityGate
from eyedx_ml.inference.uncertainty_estimator import estimate_uncertainty
from eyedx_ml.utils.config_loader import load_config
from eyedx_ml.utils.device import select_device

__all__ = ["Predictor"]


class Predictor:
    def __init__(
        self,
        model,
        labels: Sequence[str],
        *,
        model_id: str,
        model_version: str,
        device: str = "cpu",
        thresholds: Optional[Mapping[str, float]] = None,
        uncertainty_config: Optional[Mapping[str, Any]] = None,
        abstention_config: Optional[Mapping[str, Any]] = None,
        quality_config: Optional[Mapping[str, Any]] = None,
        preprocessing: Optional[Any] = None,
    ) -> None:
        if not labels:
            raise LabelUnavailableError(
                "Predictor requires an approved label vocabulary (INPUT_REQUIRED)"
            )
        self.model = model
        self.model.eval()
        self.labels = list(labels)
        self.model_id = model_id
        self.model_version = model_version
        self.device = device
        self.thresholds = dict(thresholds or {})
        self.uncertainty_config = dict(uncertainty_config or {})
        self.abstention_config = dict(abstention_config or {})
        self.quality_gate = QualityGate(**(quality_config or {})) if quality_config else None
        self.preprocessing = preprocessing

    # -- construction -------------------------------------------------------
    @classmethod
    def from_config(cls, config_path: Union[str, Path]) -> "Predictor":
        config = load_config(config_path)
        model_cfg = config.get("model", {}) or {}
        checkpoint = model_cfg.get("checkpoint")
        if not checkpoint:
            raise ArtifactUnavailableError(
                "no checkpoint configured for inference (INPUT_REQUIRED)"
            )
        path = Path(checkpoint)
        if not path.is_file():
            raise ArtifactUnavailableError(f"checkpoint not found: {path.name}")

        from eyedx_ml.models.model_config import load_model_config
        from eyedx_ml.models.model_factory import build_model
        from eyedx_ml.training.checkpoint_manager import load_checkpoint

        if not model_cfg.get("config"):
            raise NotConfiguredError("inference config requires model.config")
        model_config = load_model_config(model_cfg["config"])
        model = build_model(model_config)
        load_checkpoint(path, model=model, map_location="cpu")

        device = select_device(model_cfg.get("device", "cpu")).device
        labels = model_config.load_approved_labels() if not model_config.labels else list(model_config.labels)

        return cls(
            model,
            labels,
            model_id=model_cfg.get("model_id", "eyedx-screening"),
            model_version=str(model_cfg.get("model_version", "INPUT_REQUIRED")),
            device=device,
            thresholds=(config.get("postprocessing") or {}).get("thresholds"),
            uncertainty_config=config.get("uncertainty"),
            abstention_config=config.get("abstention"),
            quality_config=config.get("quality"),
        )

    # -- prediction ---------------------------------------------------------
    def predict(
        self,
        input_tensor,
        *,
        request_id: Optional[str] = None,
        raw_image=None,
    ) -> Dict[str, Any]:
        request_id = request_id or str(uuid.uuid4())
        start = time.perf_counter()

        quality_checks = None
        if self.quality_gate is not None and raw_image is not None:
            quality = self.quality_gate.check(raw_image)
            quality_checks = quality.to_dict()
            if not quality.passed:
                elapsed = int((time.perf_counter() - start) * 1000)
                return format_response(
                    request_id=request_id,
                    status="low_quality",
                    model_id=self.model_id,
                    model_version=self.model_version,
                    processing_time_ms=elapsed,
                    quality_checks=quality_checks,
                    abstention_reason="image failed quality checks",
                )

        try:
            import torch

            tensor = input_tensor
            if torch.is_tensor(tensor):
                tensor = tensor.to(self.device)
            with torch.no_grad():
                logits = self.model(tensor)
            if isinstance(logits, dict):
                raise NotConfiguredError("Predictor expects a single-output model")
            probs = torch.sigmoid(logits)[0].detach().cpu().numpy()
        except Exception as exc:  # pragma: no cover - runtime path
            elapsed = int((time.perf_counter() - start) * 1000)
            return format_response(
                request_id=request_id,
                status="failed",
                model_id=self.model_id,
                model_version=self.model_version,
                processing_time_ms=elapsed,
                failure_reason="inference could not be completed",
                quality_checks=quality_checks,
            )

        uncertainty = None
        if self.uncertainty_config.get("enabled", False):
            result = estimate_uncertainty(
                probs,
                method=self.uncertainty_config.get("method", "max_prob"),
                threshold=self.uncertainty_config.get("threshold"),
                model=self.model if self.uncertainty_config.get("method") == "mc_dropout" else None,
                input_tensor=input_tensor if self.uncertainty_config.get("method") == "mc_dropout" else None,
                mc_samples=int(self.uncertainty_config.get("mc_dropout_samples", 20)),
            )
            uncertainty = result.to_dict()

        elapsed = int((time.perf_counter() - start) * 1000)

        if uncertainty and uncertainty.get("is_uncertain"):
            if self.abstention_config.get("enabled", False):
                return format_response(
                    request_id=request_id,
                    status="abstained",
                    model_id=self.model_id,
                    model_version=self.model_version,
                    processing_time_ms=elapsed,
                    uncertainty=uncertainty,
                    quality_checks=quality_checks,
                    abstention_reason="model uncertainty above abstention threshold",
                )
            return format_response(
                request_id=request_id,
                status="uncertain",
                model_id=self.model_id,
                model_version=self.model_version,
                processing_time_ms=elapsed,
                predictions=format_predictions(self.labels, probs),
                uncertainty=uncertainty,
                quality_checks=quality_checks,
            )

        return format_response(
            request_id=request_id,
            status="success",
            model_id=self.model_id,
            model_version=self.model_version,
            processing_time_ms=elapsed,
            predictions=format_predictions(self.labels, probs),
            uncertainty=uncertainty,
            quality_checks=quality_checks,
        )
