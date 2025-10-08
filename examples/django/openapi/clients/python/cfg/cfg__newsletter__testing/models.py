from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class TestEmailRequest(BaseModel):
    """Simple serializer for test email.

Request model (no read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    email: str = Field(min_length=1)
    subject: str = Field(None, min_length=1, max_length=255)
    message: str = Field(None, min_length=1)



class BulkEmailResponse(BaseModel):
    """Response for bulk email sending.

Response model (includes read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    success: bool = ...
    sent_count: int = ...
    failed_count: int = ...
    total_recipients: int = ...
    error: str = None



