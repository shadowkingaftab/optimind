"""Prediction service.

Orchestrates a screening run: consent enforcement, model selection, image
retrieval, inference, conservative post-processing and persistence.

Honesty rules enforced here:
    * A low-quality stored image never calls the model; it yields a
      ``low_quality`` result.
    * An unavailable model or inference failure yields a ``failed`` record and
      the underlying error is surfaced; no result is fabricated.
    * A successful model output may be *downgraded* to ``uncertain`` or
      ``abstained`` by conservative thresholds, never upgraded.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.audit.audit_events import ACTION_PREDICTION_CREATE, RESOURCE_PREDICTION
from app.audit.audit_logger import AuditLogger
from app.core.settings import Settings, get_settings
from app.exceptions.base import APIException, NotFoundError
from app.exceptions.validation import RequestValidationError
from app.inference import get_inference_client
from app.inference.inference_contract import InferenceResult
from app.inference.request_builder import build_request
from app.models.consent import ConsentType
from app.models.eye_image import EyeImage, QualityStatus
from app.models.model_version import ModelVersion
from app.models.prediction import Prediction, PredictionStatus, RiskLevel
from app.models.user import User
from app.postprocessing import (
    ThresholdPolicy,
    build_prediction_response,
    decide_uncertainty,
    format_confidence,
    map_score_to_risk,
)
from app.repositories.eye_image_repository import EyeImageRepository
from app.repositories.prediction_repository import PredictionRepository
from app.services.consent_service import ConsentService
from app.services.model_version_service import ModelVersionService
from app.storage import get_storage
from app.utils.datetime import utcnow

_STATUS_BY_NAME = {status.value: status for status in PredictionStatus}


@dataclass(frozen=True)
class PredictionOutcome:
    prediction: Prediction
    response: dict[str, Any]


def _extension_for_media_type(media_type: str | None) -> str:
    if media_type == "image/png":
        return ".png"
    return ".jpg"


def _uncertainty_value(payload: Optional[dict[str, Any]]) -> Optional[float]:
    if not isinstance(payload, dict):
        return None
    for key in ("score", "value", "uncertainty"):
        raw = payload.get(key)
        if isinstance(raw, (int, float)):
            return float(raw)
    return None


class PredictionService:
    """Runs and records screening predictions."""

    def __init__(
        self,
        session: AsyncSession,
        *,
        settings: Optional[Settings] = None,
        threshold_policy: Optional[ThresholdPolicy] = None,
    ) -> None:
        self._session = session
        self._settings = settings or get_settings()
        self._policy = threshold_policy or ThresholdPolicy()
        self._predictions = PredictionRepository(session)
        self._images = EyeImageRepository(session)
        self._consents = ConsentService(session)
        self._models = ModelVersionService(session)
        self._audit = AuditLogger(session)

    async def predict(
        self,
        *,
        patient_id: uuid.UUID,
        eye_image_id: uuid.UUID,
        actor: Optional[User] = None,
        request_id: Optional[str] = None,
    ) -> PredictionOutcome:
        consent = None
        if self._settings.consent_required:
            consent = await self._consents.require_active(
                patient_id, consent_type=ConsentType.SCREENING
            )

        model = await self._models.require_active()

        image = await self._images.get(eye_image_id)
        if image is None or image.patient_id != patient_id:
            raise NotFoundError("The requested image was not found for this patient.")

        if image.quality_status == QualityStatus.INSUFFICIENT:
            return await self._record_low_quality(
                patient_id=patient_id,
                image=image,
                model=model,
                consent_id=consent.id if consent else None,
                actor=actor,
                request_id=request_id,
            )

        client = get_inference_client()
        consent_token = str(consent.id) if consent else "consent_not_required"
        inference_request = build_request(
            image_bytes=await self._load_bytes(image),
            consent_id=consent_token,
            image_ext=_extension_for_media_type(image.media_type),
            request_id=request_id,
        )

        started = utcnow()
        try:
            result = await client.predict(inference_request)
        except APIException as exc:
            await self._record_failure(
                patient_id=patient_id,
                image=image,
                model=model,
                consent_id=consent.id if consent else None,
                actor=actor,
                error_code=getattr(exc, "error_code", "inference_error"),
            )
            raise
        completed = utcnow()

        return await self._persist_result(
            patient_id=patient_id,
            image=image,
            model=model,
            model_id=result.model_id,
            result=result,
            consent_id=consent.id if consent else None,
            actor=actor,
            request_id=request_id,
            started_at=started,
            completed_at=completed,
        )

    async def _load_bytes(self, image: EyeImage) -> bytes:
        if not image.storage_key:
            raise RequestValidationError("The image has no stored object.")
        return await get_storage().get(image.storage_key)

    def _apply_conservative_policy(
        self, result: InferenceResult, confidence: Optional[float]
    ) -> tuple[PredictionStatus, Optional[str]]:
        status = _STATUS_BY_NAME.get(result.status, PredictionStatus.FAILED)
        if status is not PredictionStatus.SUCCESS:
            return status, result.abstention_reason or result.failure_reason
        decision = decide_uncertainty(
            confidence, _uncertainty_value(result.uncertainty), self._policy
        )
        if decision.abstain:
            return PredictionStatus.ABSTAINED, decision.reason
        if decision.uncertain:
            return PredictionStatus.UNCERTAIN, decision.reason
        if (
            confidence is not None
            and confidence < self._policy.min_confidence_for_success
        ):
            return PredictionStatus.UNCERTAIN, "confidence_below_success_threshold"
        return PredictionStatus.SUCCESS, None

    async def _persist_result(
        self,
        *,
        patient_id: uuid.UUID,
        image: EyeImage,
        model: ModelVersion,
        model_id: str,
        result: InferenceResult,
        consent_id: Optional[uuid.UUID],
        actor: Optional[User],
        request_id: Optional[str],
        started_at,
        completed_at,
    ) -> PredictionOutcome:
        formatted = format_confidence(result.predictions)
        confidence = formatted.confidence
        status, reason = self._apply_conservative_policy(result, confidence)

        items: list[dict[str, Any]] = []
        if status is PredictionStatus.SUCCESS:
            for index, item in enumerate(result.predictions):
                score = item.get("score")
                items.append(
                    {
                        "condition_code": str(item.get("label", "")),
                        "condition_label": str(item.get("label", "")),
                        "score": float(score) if score is not None else None,
                        "risk_level": map_score_to_risk(score),
                        "rank": index,
                    }
                )

        risk_level = (
            map_score_to_risk(confidence)
            if status is PredictionStatus.SUCCESS
            else RiskLevel.UNKNOWN
        )
        outcome_label = (
            formatted.top_label if status is PredictionStatus.SUCCESS else None
        )

        prediction = await self._predictions.create(
            patient_id=patient_id,
            status=status,
            eye_image_id=image.id,
            model_version_id=model.id,
            consent_id=consent_id,
            requested_by_user_id=actor.id if actor else None,
            outcome_label=outcome_label,
            risk_level=risk_level,
            confidence=confidence,
            uncertainty=_uncertainty_value(result.uncertainty),
            model_version_label=result.model_version,
            latency_ms=result.processing_time_ms,
            error_code=None,
            started_at=started_at,
            completed_at=completed_at,
            items=items,
        )
        await self._audit.record(
            ACTION_PREDICTION_CREATE,
            actor_user_id=actor.id if actor else None,
            resource_type=RESOURCE_PREDICTION,
            resource_id=str(prediction.id),
            metadata={"status": str(status), "model_version": result.model_version},
        )
        await self._session.commit()

        response = build_prediction_response(
            request_id=request_id or str(prediction.id),
            status=status,
            model_id=model_id,
            model_version=result.model_version,
            processing_time_ms=result.processing_time_ms,
            predictions=[
                {"label": item["condition_code"], "score": item["score"]}
                for item in items
                if item["score"] is not None
            ],
            uncertainty=result.uncertainty,
            explanation=result.explanation if self._settings.feature_explainability else None,
            quality_checks=result.quality_checks,
            abstention_reason=reason if status is not PredictionStatus.SUCCESS else None,
            failure_reason=result.failure_reason,
        )
        return PredictionOutcome(prediction=prediction, response=response)

    async def _record_low_quality(
        self,
        *,
        patient_id: uuid.UUID,
        image: EyeImage,
        model: ModelVersion,
        consent_id: Optional[uuid.UUID],
        actor: Optional[User],
        request_id: Optional[str],
    ) -> PredictionOutcome:
        prediction = await self._predictions.create(
            patient_id=patient_id,
            status=PredictionStatus.LOW_QUALITY,
            eye_image_id=image.id,
            model_version_id=model.id,
            consent_id=consent_id,
            requested_by_user_id=actor.id if actor else None,
            risk_level=RiskLevel.UNKNOWN,
            model_version_label=model.version,
            error_code=None,
        )
        await self._audit.record(
            ACTION_PREDICTION_CREATE,
            actor_user_id=actor.id if actor else None,
            resource_type=RESOURCE_PREDICTION,
            resource_id=str(prediction.id),
            metadata={"status": "low_quality"},
        )
        await self._session.commit()
        response = build_prediction_response(
            request_id=request_id or str(prediction.id),
            status=PredictionStatus.LOW_QUALITY,
            model_id="none",
            model_version=model.version,
            processing_time_ms=0,
            quality_checks={"acceptable": False},
            abstention_reason="image_quality_insufficient",
        )
        return PredictionOutcome(prediction=prediction, response=response)

    async def _record_failure(
        self,
        *,
        patient_id: uuid.UUID,
        image: EyeImage,
        model: ModelVersion,
        consent_id: Optional[uuid.UUID],
        actor: Optional[User],
        error_code: str,
    ) -> None:
        prediction = await self._predictions.create(
            patient_id=patient_id,
            status=PredictionStatus.FAILED,
            eye_image_id=image.id,
            model_version_id=model.id,
            consent_id=consent_id,
            requested_by_user_id=actor.id if actor else None,
            risk_level=RiskLevel.UNKNOWN,
            model_version_label=model.version,
            error_code=error_code,
        )
        await self._audit.record(
            ACTION_PREDICTION_CREATE,
            actor_user_id=actor.id if actor else None,
            resource_type=RESOURCE_PREDICTION,
            resource_id=str(prediction.id),
            metadata={"status": "failed", "error_code": error_code},
        )
        await self._session.commit()

    async def count_for_patient(self, patient_id: uuid.UUID) -> int:
        return await self._predictions.count_for_patient(patient_id)

    async def get(self, prediction_id: uuid.UUID) -> Prediction:
        prediction = await self._predictions.get(prediction_id)
        if prediction is None:
            raise NotFoundError("The requested prediction was not found.")
        return prediction
