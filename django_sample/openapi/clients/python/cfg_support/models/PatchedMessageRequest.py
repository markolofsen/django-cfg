from typing import *

from pydantic import BaseModel, Field


class PatchedMessageRequest(BaseModel):
    """
    None model

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    text: Optional[str] = Field(validation_alias="text", default=None)
