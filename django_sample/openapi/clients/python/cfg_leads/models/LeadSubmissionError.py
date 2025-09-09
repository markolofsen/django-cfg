from typing import *

from pydantic import BaseModel, Field


class LeadSubmissionError(BaseModel):
    """
    None model
        Response serializer for lead submission errors.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    success: bool = Field(validation_alias="success")

    error: str = Field(validation_alias="error")

    details: Optional[Dict[str, Any]] = Field(validation_alias="details", default=None)
