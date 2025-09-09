from typing import *

from pydantic import BaseModel, Field


class LeadSubmissionResponse(BaseModel):
    """
    None model
        Response serializer for successful lead submission.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    success: bool = Field(validation_alias="success")

    message: str = Field(validation_alias="message")

    lead_id: int = Field(validation_alias="lead_id")
