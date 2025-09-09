from typing import *

from pydantic import BaseModel, Field

from .ContactTypeEnum import ContactTypeEnum


class LeadSubmission(BaseModel):
    """
    None model
        Serializer for lead form submission from frontend.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    name: str = Field(validation_alias="name")

    email: str = Field(validation_alias="email")

    company: Optional[str] = Field(validation_alias="company", default=None)

    company_site: Optional[str] = Field(validation_alias="company_site", default=None)

    contact_type: Optional[ContactTypeEnum] = Field(validation_alias="contact_type", default=None)

    contact_value: Optional[str] = Field(validation_alias="contact_value", default=None)

    subject: Optional[str] = Field(validation_alias="subject", default=None)

    message: str = Field(validation_alias="message")

    extra: Optional[Any] = Field(validation_alias="extra", default=None)

    site_url: str = Field(validation_alias="site_url")
