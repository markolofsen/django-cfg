from typing import *

from pydantic import BaseModel, Field

from .UserActivity import UserActivity


class PaginatedUserActivityList(BaseModel):
    """
    None model

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    count: int = Field(validation_alias="count")

    next: Optional[str] = Field(validation_alias="next", default=None)

    previous: Optional[str] = Field(validation_alias="previous", default=None)

    results: List[UserActivity] = Field(validation_alias="results")
