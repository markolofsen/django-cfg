from typing import *

from pydantic import BaseModel, Field

from .StatusEnum import StatusEnum


class Ticket(BaseModel):
    """
    None model

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    uuid: str = Field(validation_alias="uuid")

    user: int = Field(validation_alias="user")

    subject: str = Field(validation_alias="subject")

    status: Optional[StatusEnum] = Field(validation_alias="status", default=None)

    created_at: str = Field(validation_alias="created_at")

    unanswered_messages_count: int = Field(validation_alias="unanswered_messages_count")
