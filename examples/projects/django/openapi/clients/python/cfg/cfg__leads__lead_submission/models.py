from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from ..enums import LeadSubmissionRequestcontact_type


class LeadSubmissionResponse(BaseModel):
    """
    Response serializer for successful lead submission.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    success: bool = ...
    message: str = ...
    lead_id: int = ...



class LeadSubmissionError(BaseModel):
    """
    Response serializer for lead submission errors.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    success: bool = ...
    error: str = ...
    details: dict[str, Any] = None



class LeadSubmissionRequest(BaseModel):
    """
    Serializer for lead form submission from frontend.

    Request model (no read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    name: str = Field(min_length=1, max_length=200)
    email: str = Field(min_length=1, max_length=254)
    company: str | None = Field(None, max_length=200)
    company_site: str | None = Field(None, max_length=200)
    contact_type: LeadSubmissionRequestContactType = Field(None, description='* `email` - Email\n* `whatsapp` - WhatsApp\n* `telegram` - Telegram\n* `phone` - Phone\n* `other` - Other')
    contact_value: str | None = Field(None, max_length=200)
    subject: str | None = Field(None, max_length=200)
    message: str = Field(min_length=1)
    extra: str | None = None
    site_url: str = Field(description='Frontend URL where form was submitted', min_length=1, max_length=200)



