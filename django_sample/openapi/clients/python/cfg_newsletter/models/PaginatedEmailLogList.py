from typing import *

from pydantic import BaseModel, Field

from .EmailLog import EmailLog


class PaginatedEmailLogList(BaseModel):
    """
    None model

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    count: int = Field(validation_alias="count")

    next: Optional[str] = Field(validation_alias="next", default=None)

    previous: Optional[str] = Field(validation_alias="previous", default=None)

    results: List[EmailLog] = Field(validation_alias="results")
