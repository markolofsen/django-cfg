from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class BulkEmailResponse(BaseModel):
    """
    Response for bulk email sending.

    Response model (includes read-only fields).
    """

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



class BulkEmailRequest(BaseModel):
    """
    Simple serializer for bulk email.

    Request model (no read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    recipients: list[str] = ...
    subject: str = Field(min_length=1, max_length=255)
    email_title: str = Field(min_length=1, max_length=255)
    main_text: str = Field(min_length=1)
    main_html_content: str = None
    button_text: str = Field(None, max_length=100)
    button_url: str = None
    secondary_text: str = None



