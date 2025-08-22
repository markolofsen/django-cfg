from typing import *

from pydantic import BaseModel, Field

from .Comment import Comment


class PaginatedCommentList(BaseModel):
    """
    None model

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    count: int = Field(validation_alias="count")

    next: Optional[str] = Field(validation_alias="next", default=None)

    previous: Optional[str] = Field(validation_alias="previous", default=None)

    results: List[Comment] = Field(validation_alias="results")
