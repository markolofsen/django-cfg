from typing import *

from pydantic import BaseModel, Field

from .ContactTypeEnum import ContactTypeEnum


class PatchedLeadSubmissionRequest(BaseModel):
    """
    None model
        Serializer for lead form submission from frontend.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    name: Optional[str] = Field(validation_alias="name", default=None)

    email: Optional[str] = Field(validation_alias="email", default=None)

    company: Optional[str] = Field(validation_alias="company", default=None)

    company_site: Optional[str] = Field(validation_alias="company_site", default=None)

    contact_type: Optional[ContactTypeEnum] = Field(validation_alias="contact_type", default=None)

    contact_value: Optional[str] = Field(validation_alias="contact_value", default=None)

    subject: Optional[str] = Field(validation_alias="subject", default=None)

    message: Optional[str] = Field(validation_alias="message", default=None)

    extra: Optional[Any] = Field(validation_alias="extra", default=None)

    site_url: Optional[str] = Field(validation_alias="site_url", default=None)
