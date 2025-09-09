from typing import *

from pydantic import BaseModel, Field

from .User import User


class OTPVerifyResponse(BaseModel):
    """
    None model
        OTP verification response.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    refresh: str = Field(validation_alias="refresh")

    access: str = Field(validation_alias="access")

    user: User = Field(validation_alias="user")
