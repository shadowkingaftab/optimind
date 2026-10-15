"""Model version schemas.

Mirrors ``model-metadata.schema.json``. Performance metrics are not part of
these schemas: they must come from verified evaluation, never be invented.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class ModelCapabilities(BaseModel):
    model_config = ConfigDict(extra="ignore")

    supports_uncertainty: bool = False
    supports_explanation: bool = False
    supports_abstention: bool = False


class ModelVersionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    version: str
    name: str
    status: str
    is_active: bool
    approved_at: Optional[datetime] = None
    created_at: datetime


class ModelVersionRegister(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: str = Field(min_length=1, max_length=64)
    name: str = Field(default="", max_length=128)
    artifact_uri: Optional[str] = Field(default=None, max_length=1024)
    checksum: Optional[str] = Field(default=None, max_length=128)
    input_contract_version: Optional[str] = Field(default=None, max_length=32)
    output_contract_version: Optional[str] = Field(default=None, max_length=32)
    metadata: Optional[dict[str, Any]] = None


class ModelMetadata(BaseModel):
    """Model metadata as defined by the shared contract."""

    model_config = ConfigDict(extra="forbid")

    model_id: str
    model_version: str
    created_at: datetime
    labels: list[str] = Field(default_factory=list)
    preprocessing: dict[str, Any] = Field(default_factory=dict)
    capabilities: ModelCapabilities = Field(default_factory=ModelCapabilities)
    description: Optional[str] = None
