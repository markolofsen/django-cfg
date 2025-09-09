from typing import *

from pydantic import BaseModel, Field


class TestEmailRequest(BaseModel):
    """
    None model
        Simple serializer for test email.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    email: str = Field(validation_alias="email")

    subject: Optional[str] = Field(validation_alias="subject", default=None)

    message: Optional[str] = Field(validation_alias="message", default=None)
