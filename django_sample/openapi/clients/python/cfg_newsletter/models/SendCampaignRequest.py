from typing import *

from pydantic import BaseModel, Field


class SendCampaignRequest(BaseModel):
    """
    None model
        Simple serializer for sending campaign.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    campaign_id: int = Field(validation_alias="campaign_id")
