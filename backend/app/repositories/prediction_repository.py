"""Prediction persistence."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional, Sequence

from sqlalchemy import func, select

from app.models.prediction import Prediction, PredictionStatus, RiskLevel
from app.models.prediction_item import PredictionItem
from app.repositories.base_repository import BaseRepository


class PredictionRepository(BaseRepository[Prediction]):
    model = Prediction

    async def create(
        self,
        *,
        patient_id: uuid.UUID,
        status: PredictionStatus,
        eye_image_id: Optional[uuid.UUID] = None,
        model_version_id: Optional[uuid.UUID] = None,
        consent_id: Optional[uuid.UUID] = None,
        requested_by_user_id: Optional[uuid.UUID] = None,
        outcome_label: Optional[str] = None,
        risk_level: Optional[RiskLevel] = None,
        confidence: Optional[float] = None,
        uncertainty: Optional[float] = None,
        quality_score: Optional[float] = None,
        model_version_label: Optional[str] = None,
        latency_ms: Optional[int] = None,
        error_code: Optional[str] = None,
        started_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None,
        items: Optional[Sequence[dict[str, Any]]] = None,
    ) -> Prediction:
        prediction = Prediction(
            patient_id=patient_id,
            status=status,
            eye_image_id=eye_image_id,
            model_version_id=model_version_id,
            consent_id=consent_id,
            requested_by_user_id=requested_by_user_id,
            outcome_label=outcome_label,
            risk_level=risk_level,
            confidence=confidence,
            uncertainty=uncertainty,
            quality_score=quality_score,
            model_version_label=model_version_label,
            latency_ms=latency_ms,
            error_code=error_code,
            started_at=started_at,
            completed_at=completed_at,
        )
        self.session.add(prediction)
        await self.session.flush()

        for index, item in enumerate(items or ()):
            self.session.add(
                PredictionItem(
                    prediction_id=prediction.id,
                    condition_code=str(item.get("condition_code", "")),
                    condition_label=item.get("condition_label"),
                    score=item.get("score"),
                    threshold=item.get("threshold"),
                    risk_level=item.get("risk_level"),
                    rank=item.get("rank", index),
                )
            )
        await self.session.flush()
        return prediction

    async def list_for_patient(
        self,
        patient_id: uuid.UUID,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> Sequence[Prediction]:
        stmt = (
            select(Prediction)
            .where(Prediction.patient_id == patient_id)
            .order_by(Prediction.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return (await self.session.execute(stmt)).scalars().all()

    async def list_recent(
        self,
        *,
        limit: int = 100,
        offset: int = 0,
        status: Optional[PredictionStatus] = None,
    ) -> Sequence[Prediction]:
        stmt = select(Prediction).order_by(Prediction.created_at.desc())
        if status is not None:
            stmt = stmt.where(Prediction.status == status)
        stmt = stmt.offset(offset).limit(limit)
        return (await self.session.execute(stmt)).scalars().all()

    async def count_for_patient(self, patient_id: uuid.UUID) -> int:
        stmt = select(func.count()).select_from(Prediction).where(
            Prediction.patient_id == patient_id
        )
        return int((await self.session.execute(stmt)).scalar() or 0)
