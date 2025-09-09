from typing import *

from pydantic import BaseModel, Field

from .EmailLogStatusEnum import EmailLogStatusEnum


class EmailLog(BaseModel):
    """
    None model
        Serializer for EmailLog model.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    id: int = Field(validation_alias="id")

    user: int = Field(validation_alias="user")

    user_email: str = Field(validation_alias="user_email")

    newsletter: int = Field(validation_alias="newsletter")

    newsletter_title: str = Field(validation_alias="newsletter_title")

    recipient: str = Field(validation_alias="recipient")

    subject: str = Field(validation_alias="subject")

    body: str = Field(validation_alias="body")

    status: EmailLogStatusEnum = Field(validation_alias="status")

    created_at: str = Field(validation_alias="created_at")

    sent_at: str = Field(validation_alias="sent_at")

    error_message: str = Field(validation_alias="error_message")
