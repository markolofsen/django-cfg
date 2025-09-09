from typing import *

from pydantic import BaseModel, Field

from .StatusEnum import StatusEnum


class PatchedTicketRequest(BaseModel):
    """
    None model

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    user: Optional[int] = Field(validation_alias="user", default=None)

    subject: Optional[str] = Field(validation_alias="subject", default=None)

    status: Optional[StatusEnum] = Field(validation_alias="status", default=None)
