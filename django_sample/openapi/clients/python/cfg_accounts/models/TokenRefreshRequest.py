from typing import *

from pydantic import BaseModel, Field


class TokenRefreshRequest(BaseModel):
    """
    None model

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    refresh: str = Field(validation_alias="refresh")
