from typing import *

from pydantic import BaseModel, Field


class Unsubscribe(BaseModel):
    """
    None model
        Simple serializer for unsubscribe.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    subscription_id: int = Field(validation_alias="subscription_id")
