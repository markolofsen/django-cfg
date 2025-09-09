from typing import *

from pydantic import BaseModel, Field


class OTPRequestResponse(BaseModel):
    """
    None model
        OTP request response.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    message: str = Field(validation_alias="message")
