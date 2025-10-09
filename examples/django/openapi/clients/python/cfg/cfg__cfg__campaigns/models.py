from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from ..enums import NewsletterCampaignstatus


class PaginatedNewsletterCampaignList(BaseModel):
    """
    
    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
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
    results: list[dict[str, Any]] = Field(description='Array of items for current page')



class NewsletterCampaign(BaseModel):
    """
    Serializer for NewsletterCampaign model.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    id: int = ...
    newsletter: int = ...
    newsletter_title: str = ...
    subject: str = Field(max_length=255)
    email_title: str = Field(max_length=255)
    main_text: str = ...
    main_html_content: str = None
    button_text: str = Field(None, max_length=100)
    button_url: str = Field(None, max_length=200)
    secondary_text: str = None
    status: NewsletterCampaignStatus = Field(description='* `draft` - Draft\n* `sending` - Sending\n* `sent` - Sent\n* `failed` - Failed')
    created_at: str = ...
    sent_at: str | None = ...
    recipient_count: int = ...



class SendCampaignResponse(BaseModel):
    """
    Response for sending campaign.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    success: bool = ...
    message: str = None
    sent_count: int = None
    error: str = None



class ErrorResponse(BaseModel):
    """
    Generic error response.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    success: bool = None
    message: str = ...



class NewsletterCampaignRequest(BaseModel):
    """
    Serializer for NewsletterCampaign model.

    Request model (no read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    newsletter: int = ...
    subject: str = Field(min_length=1, max_length=255)
    email_title: str = Field(min_length=1, max_length=255)
    main_text: str = Field(min_length=1)
    main_html_content: str = None
    button_text: str = Field(None, max_length=100)
    button_url: str = Field(None, max_length=200)
    secondary_text: str = None



class SendCampaignRequest(BaseModel):
    """
    Simple serializer for sending campaign.

    Request model (no read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    campaign_id: int = ...



