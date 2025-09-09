from typing import *

from pydantic import BaseModel, Field


class PatchedNewsletterCampaignRequest(BaseModel):
    """
    None model
        Serializer for NewsletterCampaign model.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    newsletter: Optional[int] = Field(validation_alias="newsletter", default=None)

    subject: Optional[str] = Field(validation_alias="subject", default=None)

    email_title: Optional[str] = Field(validation_alias="email_title", default=None)

    main_text: Optional[str] = Field(validation_alias="main_text", default=None)

    main_html_content: Optional[str] = Field(validation_alias="main_html_content", default=None)

    button_text: Optional[str] = Field(validation_alias="button_text", default=None)

    button_url: Optional[str] = Field(validation_alias="button_url", default=None)

    secondary_text: Optional[str] = Field(validation_alias="secondary_text", default=None)
