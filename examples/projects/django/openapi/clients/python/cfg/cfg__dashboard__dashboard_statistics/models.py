from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class UserStatistics(BaseModel):
    """
    Serializer for user statistics.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    total_users: int = Field(description='Total number of users')
    active_users: int = Field(description='Active users (last 30 days)')
    new_users: int = Field(description='New users (last 7 days)')
    superusers: int = Field(description='Number of superusers')



