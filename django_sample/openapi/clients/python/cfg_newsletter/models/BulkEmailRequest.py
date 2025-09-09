from typing import *

from pydantic import BaseModel, Field


class BulkEmailRequest(BaseModel):
    """
    None model
        Simple serializer for bulk email.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    recipients: List[str] = Field(validation_alias="recipients")

    subject: str = Field(validation_alias="subject")

    email_title: str = Field(validation_alias="email_title")

    main_text: str = Field(validation_alias="main_text")

    main_html_content: Optional[str] = Field(validation_alias="main_html_content", default=None)

    button_text: Optional[str] = Field(validation_alias="button_text", default=None)

    button_url: Optional[str] = Field(validation_alias="button_url", default=None)

    secondary_text: Optional[str] = Field(validation_alias="secondary_text", default=None)
