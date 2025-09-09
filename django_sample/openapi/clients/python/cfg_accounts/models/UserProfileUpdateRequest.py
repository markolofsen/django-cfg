from typing import *

from pydantic import BaseModel, Field


class UserProfileUpdateRequest(BaseModel):
    """
    None model
        Serializer for updating user profile.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    first_name: Optional[str] = Field(validation_alias="first_name", default=None)

    last_name: Optional[str] = Field(validation_alias="last_name", default=None)

    company: Optional[str] = Field(validation_alias="company", default=None)

    phone: Optional[str] = Field(validation_alias="phone", default=None)

    position: Optional[str] = Field(validation_alias="position", default=None)
