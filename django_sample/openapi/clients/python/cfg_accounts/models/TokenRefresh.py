from typing import *

from pydantic import BaseModel, Field


class TokenRefresh(BaseModel):
    """
    None model

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    access: str = Field(validation_alias="access")

    refresh: str = Field(validation_alias="refresh")
