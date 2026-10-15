"""Eye image persistence (references only; no image bytes are stored here)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional, Sequence

from sqlalchemy import select

from app.models.eye_image import EyeImage, EyeSide, QualityStatus
from app.repositories.base_repository import BaseRepository


class EyeImageRepository(BaseRepository[EyeImage]):
    model = EyeImage

    async def list_for_patient(self, patient_id: uuid.UUID) -> Sequence[EyeImage]:
        stmt = (
            select(EyeImage)
            .where(EyeImage.patient_id == patient_id)
            .order_by(EyeImage.created_at.desc())
        )
        return (await self.session.execute(stmt)).scalars().all()

    async def get_by_checksum(self, checksum: str) -> Optional[EyeImage]:
        stmt = select(EyeImage).where(EyeImage.checksum_sha256 == checksum)
        return (await self.session.execute(stmt)).scalars().first()

    async def create(
        self,
        *,
        patient_id: uuid.UUID,
        storage_key: str,
        media_type: str,
        eye_side: EyeSide = EyeSide.UNKNOWN,
        quality_status: QualityStatus = QualityStatus.UNKNOWN,
        byte_size: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        checksum_sha256: Optional[str] = None,
        captured_at: Optional[datetime] = None,
        uploaded_by_user_id: Optional[uuid.UUID] = None,
    ) -> EyeImage:
        image = EyeImage(
            patient_id=patient_id,
            storage_key=storage_key,
            media_type=media_type,
            eye_side=eye_side,
            quality_status=quality_status,
            byte_size=byte_size,
            width=width,
            height=height,
            checksum_sha256=checksum_sha256,
            captured_at=captured_at,
            uploaded_by_user_id=uploaded_by_user_id,
        )
        return await self.add(image)

    async def set_quality(
        self, image: EyeImage, quality_status: QualityStatus
    ) -> None:
        image.quality_status = quality_status
        await self.session.flush()
