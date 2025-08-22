from typing import *

from pydantic import BaseModel, Field

from .ActivityTypeEnum import ActivityTypeEnum


class UserActivityRequest(BaseModel):
    """
    None model
        Serializer for user activities.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    activity_type: ActivityTypeEnum = Field(validation_alias="activity_type")

    description: Optional[str] = Field(validation_alias="description", default=None)

    ip_address: Optional[str] = Field(validation_alias="ip_address", default=None)

    object_id: Optional[int] = Field(validation_alias="object_id", default=None)

    object_type: Optional[str] = Field(validation_alias="object_type", default=None)
