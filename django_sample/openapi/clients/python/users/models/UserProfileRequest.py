from typing import *

from pydantic import BaseModel, Field


class UserProfileRequest(BaseModel):
    """
    None model
        Serializer for user profiles.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    website: Optional[str] = Field(validation_alias="website", default=None)

    github: Optional[str] = Field(validation_alias="github", default=None)

    twitter: Optional[str] = Field(validation_alias="twitter", default=None)

    linkedin: Optional[str] = Field(validation_alias="linkedin", default=None)

    company: Optional[str] = Field(validation_alias="company", default=None)

    job_title: Optional[str] = Field(validation_alias="job_title", default=None)
