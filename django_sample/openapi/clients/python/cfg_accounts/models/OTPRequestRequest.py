from typing import *

from pydantic import BaseModel, Field


class OTPRequestRequest(BaseModel):
    """
    None model
        Serializer for OTP request.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    email: str = Field(validation_alias="email")

    source_url: Optional[str] = Field(validation_alias="source_url", default=None)
