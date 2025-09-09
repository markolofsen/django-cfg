from typing import *

from pydantic import BaseModel, Field


class OTPVerifyRequest(BaseModel):
    """
    None model
        Serializer for OTP verification.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    email: str = Field(validation_alias="email")

    otp: str = Field(validation_alias="otp")

    source_url: Optional[str] = Field(validation_alias="source_url", default=None)
