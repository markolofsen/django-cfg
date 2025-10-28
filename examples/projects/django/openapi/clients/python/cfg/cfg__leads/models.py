from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from ..enums import LeadSubmissionContactType, LeadSubmissionRequestContactType, PatchedLeadSubmissionRequestContactType


class PaginatedLeadSubmissionList(BaseModel):
    """
    
    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    count: int = Field(description='Total number of items across all pages')
    page: int = Field(description='Current page number (1-based)')
    pages: int = Field(description='Total number of pages')
    page_size: int = Field(description='Number of items per page')
    has_next: bool = Field(description='Whether there is a next page')
    has_previous: bool = Field(description='Whether there is a previous page')
    next_page: int | None = Field(None, description='Next page number (null if no next page)')
    previous_page: int | None = Field(None, description='Previous page number (null if no previous page)')
    results: list[Any] = Field(description='Array of items for current page')



class LeadSubmission(BaseModel):
    """
    Serializer for lead form submission from frontend.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    name: str = Field(max_length=200)
    email: str = Field(max_length=254)
    company: str | None = Field(None, max_length=200)
    company_site: str | None = Field(None, max_length=200)
    contact_type: LeadSubmissionContactType = Field(None, description='* `email` - Email\n* `whatsapp` - WhatsApp\n* `telegram` - Telegram\n* `phone` - Phone\n* `other` - Other')
    contact_value: str | None = Field(None, max_length=200)
    subject: str | None = Field(None, max_length=200)
    message: str = ...
    extra: str | None = None
    site_url: str = Field(description='Frontend URL where form was submitted', max_length=200)



class LeadSubmissionRequest(BaseModel):
    """
    Serializer for lead form submission from frontend.

    Request model (no read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
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



class PatchedLeadSubmissionRequest(BaseModel):
    """
    Serializer for lead form submission from frontend.

    Request model (no read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    name: str = Field(None, min_length=1, max_length=200)
    email: str = Field(None, min_length=1, max_length=254)
    company: str | None = Field(None, max_length=200)
    company_site: str | None = Field(None, max_length=200)
    contact_type: PatchedLeadSubmissionRequestContactType = Field(None, description='* `email` - Email\n* `whatsapp` - WhatsApp\n* `telegram` - Telegram\n* `phone` - Phone\n* `other` - Other')
    contact_value: str | None = Field(None, max_length=200)
    subject: str | None = Field(None, max_length=200)
    message: str = Field(None, min_length=1)
    extra: str | None = None
    site_url: str = Field(None, description='Frontend URL where form was submitted', min_length=1, max_length=200)



