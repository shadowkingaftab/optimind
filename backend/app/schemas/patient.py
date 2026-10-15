"""Patient schemas.

Identity fields are optional; the patient code is the pseudonymous reference.
No clinical values are part of these schemas.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class PatientCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    patient_code: Optional[str] = Field(default=None, max_length=64)
    display_name: Optional[str] = Field(default=None, max_length=255)
    date_of_birth: Optional[date] = None
    sex: Optional[str] = Field(default=None, max_length=32)


class PatientUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    display_name: Optional[str] = Field(default=None, max_length=255)
    date_of_birth: Optional[date] = None
    sex: Optional[str] = Field(default=None, max_length=32)


class PatientRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    patient_code: str
    display_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    sex: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ConsentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    consent_type: Literal["screening", "storage", "research"] = "screening"
    expires_at: Optional[datetime] = None
    document_ref: Optional[str] = Field(default=None, max_length=512)


class ConsentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    patient_id: uuid.UUID
    consent_type: str
    status: str
    granted_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    withdrawn_at: Optional[datetime] = None
    created_at: datetime
