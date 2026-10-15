"""Upload service.

Orchestrates the safe ingestion of an image: consent check, structural
validation, decoding, metadata stripping, quality assessment and storage.
The database stores only a reference (storage key) and structural metadata.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.audit.audit_events import ACTION_UPLOAD_CREATE, RESOURCE_EYE_IMAGE
from app.audit.audit_logger import AuditLogger
from app.core.constants import ALLOWED_IMAGE_EXTENSIONS, ALLOWED_IMAGE_MEDIA_TYPES
from app.core.settings import Settings, get_settings
from app.exceptions.validation import ImageQualityError
from app.models.consent import ConsentType
from app.models.eye_image import EyeImage, EyeSide, QualityStatus
from app.models.user import User
from app.postprocessing.threshold_policy import ThresholdPolicy
from app.preprocessing import (
    QualityResult,
    assess_quality,
    decode_image,
    extract_metadata,
    sanitize_image,
    validate_upload,
)
from app.preprocessing.preprocessing_contract import PreprocessedImage
from app.repositories.eye_image_repository import EyeImageRepository
from app.services.consent_service import ConsentService
from app.storage import get_storage
from app.storage.file_naming import build_key
from app.utils.identifiers import new_uuid_str


@dataclass(frozen=True)
class UploadResult:
    image: EyeImage
    quality: QualityResult
    sanitized: PreprocessedImage


class UploadService:
    """Validates, sanitizes and persists uploaded images."""

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
        self._images = EyeImageRepository(session)
        self._consents = ConsentService(session)
        self._audit = AuditLogger(session)

    async def create_upload(
        self,
        *,
        patient_id,
        data: bytes,
        filename: Optional[str],
        content_type: Optional[str],
        eye_side: EyeSide = EyeSide.UNKNOWN,
        actor: Optional[User] = None,
        reject_low_quality: bool = False,
        enforce_consent: Optional[bool] = None,
    ) -> UploadResult:
        require_consent = (
            self._settings.consent_required
            if enforce_consent is None
            else enforce_consent
        )
        if require_consent:
            await self._consents.require_active(
                patient_id, consent_type=ConsentType.STORAGE
            )

        validated = validate_upload(
            filename=filename,
            content_type=content_type,
            data=data,
            allowed_extensions=ALLOWED_IMAGE_EXTENSIONS,
            allowed_media_types=ALLOWED_IMAGE_MEDIA_TYPES,
            max_bytes=self._settings.max_upload_mb * 1024 * 1024,
        )

        image = decode_image(data)
        extract_metadata(image)
        quality = assess_quality(image, self._policy)
        if reject_low_quality and not quality.acceptable:
            raise ImageQualityError(issues=quality.issues)

        sanitized = sanitize_image(image)
        key = build_key(
            prefix="images",
            owner_id=str(patient_id),
            extension=".jpg",
            unique=new_uuid_str(),
        )
        stored = await get_storage().put(
            key, sanitized.data, content_type=sanitized.media_type
        )

        eye_image = await self._images.create(
            patient_id=patient_id,
            storage_key=stored.key,
            media_type=sanitized.media_type,
            eye_side=eye_side,
            quality_status=(
                QualityStatus.ACCEPTABLE
                if quality.acceptable
                else QualityStatus.INSUFFICIENT
            ),
            byte_size=stored.size_bytes,
            width=sanitized.width,
            height=sanitized.height,
            checksum_sha256=sanitized.checksum_sha256 or stored.checksum_sha256,
            uploaded_by_user_id=actor.id if actor else None,
        )
        await self._audit.record(
            ACTION_UPLOAD_CREATE,
            actor_user_id=actor.id if actor else None,
            resource_type=RESOURCE_EYE_IMAGE,
            resource_id=str(eye_image.id),
            metadata={
                "quality_status": str(eye_image.quality_status),
                "extension": validated.extension,
            },
        )
        await self._session.commit()
        return UploadResult(image=eye_image, quality=quality, sanitized=sanitized)
