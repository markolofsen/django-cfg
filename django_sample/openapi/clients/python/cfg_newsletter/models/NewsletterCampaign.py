from typing import *

from pydantic import BaseModel, Field

from .NewsletterCampaignStatusEnum import NewsletterCampaignStatusEnum


class NewsletterCampaign(BaseModel):
    """
    None model
        Serializer for NewsletterCampaign model.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    id: int = Field(validation_alias="id")

    newsletter: int = Field(validation_alias="newsletter")

    newsletter_title: str = Field(validation_alias="newsletter_title")

    subject: str = Field(validation_alias="subject")

    email_title: str = Field(validation_alias="email_title")

    main_text: str = Field(validation_alias="main_text")

    main_html_content: Optional[str] = Field(validation_alias="main_html_content", default=None)

    button_text: Optional[str] = Field(validation_alias="button_text", default=None)

    button_url: Optional[str] = Field(validation_alias="button_url", default=None)

    secondary_text: Optional[str] = Field(validation_alias="secondary_text", default=None)

    status: NewsletterCampaignStatusEnum = Field(validation_alias="status")

    created_at: str = Field(validation_alias="created_at")

    sent_at: str = Field(validation_alias="sent_at")

    recipient_count: int = Field(validation_alias="recipient_count")
