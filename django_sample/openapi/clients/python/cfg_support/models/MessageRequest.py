from typing import *

from pydantic import BaseModel, Field


class MessageRequest(BaseModel):
    """
    None model

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    text: str = Field(validation_alias="text")
