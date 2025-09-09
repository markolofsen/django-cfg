from typing import *

from pydantic import BaseModel, Field


class SubscribeRequest(BaseModel):
    """
    None model
        Simple serializer for newsletter subscription.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    newsletter_id: int = Field(validation_alias="newsletter_id")

    email: str = Field(validation_alias="email")
