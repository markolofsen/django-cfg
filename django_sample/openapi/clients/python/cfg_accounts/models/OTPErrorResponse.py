from typing import *

from pydantic import BaseModel, Field


class OTPErrorResponse(BaseModel):
    """
    None model
        Error response for OTP operations.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    error: str = Field(validation_alias="error")
