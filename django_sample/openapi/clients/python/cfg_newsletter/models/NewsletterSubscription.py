from typing import *

from pydantic import BaseModel, Field


class NewsletterSubscription(BaseModel):
    """
    None model
        Serializer for NewsletterSubscription model.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    id: int = Field(validation_alias="id")

    newsletter: int = Field(validation_alias="newsletter")

    newsletter_title: str = Field(validation_alias="newsletter_title")

    user: Optional[int] = Field(validation_alias="user", default=None)

    user_email: str = Field(validation_alias="user_email")

    email: str = Field(validation_alias="email")

    is_active: Optional[bool] = Field(validation_alias="is_active", default=None)

    subscribed_at: str = Field(validation_alias="subscribed_at")

    unsubscribed_at: str = Field(validation_alias="unsubscribed_at")
