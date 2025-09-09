from typing import *

from pydantic import BaseModel, Field

from .Sender import Sender


class Message(BaseModel):
    """
    None model

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    uuid: str = Field(validation_alias="uuid")

    ticket: str = Field(validation_alias="ticket")

    sender: Sender = Field(validation_alias="sender")

    is_from_author: bool = Field(validation_alias="is_from_author")

    text: str = Field(validation_alias="text")

    created_at: str = Field(validation_alias="created_at")
