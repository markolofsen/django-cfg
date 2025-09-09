from typing import *

from pydantic import BaseModel, Field

from .StatusEnum import StatusEnum


class TicketRequest(BaseModel):
    """
    None model

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    user: int = Field(validation_alias="user")

    subject: str = Field(validation_alias="subject")

    status: Optional[StatusEnum] = Field(validation_alias="status", default=None)
