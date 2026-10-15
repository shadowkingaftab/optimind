"""Error response schemas.

These mirror the shared ErrorResponse contract
(``contracts/json-schemas/error-response.schema.json``) exactly. Route code
should raise ``app.exceptions`` types; the exception handlers render the
body below.
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

class ErrorResponse(BaseModel):
    """Structured error payload returned for every failed request."""

    model_config = ConfigDict(extra="forbid")

    error: str = Field(
        ..., description="Machine-readable error code (snake_case)."
    )
    message: str = Field(
        ..., description="Human-readable, screening-safe message."
    )
    request_id: str = Field(
        ..., description="Traceable request identifier (UUID)."
    )
    details: Optional[dict[str, Any]] = Field(
        default=None,
        description="Additional non-sensitive structured details.",
    )


class ValidationIssue(BaseModel):
    """A single validation problem, used inside ``details.issues``."""

    model_config = ConfigDict(extra="forbid")

    loc: list[str] = Field(default_factory=list)
    msg: str
    type: str = "value_error"
