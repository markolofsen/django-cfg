from typing import *

from pydantic import BaseModel, Field

from .UserList import UserList


class UserStats(BaseModel):
    """
    None model
        Serializer for user statistics.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    total_users: int = Field(validation_alias="total_users")

    active_users: int = Field(validation_alias="active_users")

    new_users_today: int = Field(validation_alias="new_users_today")

    new_users_this_week: int = Field(validation_alias="new_users_this_week")

    new_users_this_month: int = Field(validation_alias="new_users_this_month")

    top_users: List[UserList] = Field(validation_alias="top_users")
