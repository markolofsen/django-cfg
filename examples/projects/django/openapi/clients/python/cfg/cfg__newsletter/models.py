from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from ..enums import NewsletterCampaignStatus


class NewsletterCampaign(BaseModel):
    """
    Serializer for NewsletterCampaign model.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    id: int = ...
    newsletter: int = ...
    newsletter_title: Any = ...
    subject: str = Field(max_length=255)
    email_title: str = Field(max_length=255)
    main_text: str = ...
    main_html_content: str = None
    button_text: str = Field(None, max_length=100)
    button_url: str = Field(None, max_length=200)
    secondary_text: str = None
    status: NewsletterCampaignStatus = Field(description='* `draft` - Draft\n* `sending` - Sending\n* `sent` - Sent\n* `failed` - Failed')
    created_at: Any = ...
    sent_at: Any | None = ...
    recipient_count: int = ...



class Unsubscribe(BaseModel):
    """
    Simple serializer for unsubscribe.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    subscription_id: int = ...



class PatchedNewsletterCampaignRequest(BaseModel):
    """
    Serializer for NewsletterCampaign model.

    Request model (no read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    newsletter: int = None
    subject: str = Field(None, min_length=1, max_length=255)
    email_title: str = Field(None, min_length=1, max_length=255)
    main_text: str = Field(None, min_length=1)
    main_html_content: str = None
    button_text: str = Field(None, max_length=100)
    button_url: str = Field(None, max_length=200)
    secondary_text: str = None



class UnsubscribeRequest(BaseModel):
    """
    Simple serializer for unsubscribe.

    Request model (no read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    subscription_id: int = ...



class PatchedUnsubscribeRequest(BaseModel):
    """
    Simple serializer for unsubscribe.

    Request model (no read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    subscription_id: int = None



