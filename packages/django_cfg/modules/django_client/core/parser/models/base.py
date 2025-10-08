"""
OpenAPI Input Models - Base types.

These models represent the raw OpenAPI specification structure as it appears
in the JSON/YAML file. They are version-agnostic where possible.

Reference: https://spec.openapis.org/oas/v3.1.0
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ContactObject(BaseModel):
    """
    OpenAPI Contact Object.

    Reference: https://spec.openapis.org/oas/v3.1.0#contact-object
    """

    model_config = ConfigDict(extra="allow")

    name: str | None = None
    url: str | None = None
    email: str | None = None


class LicenseObject(BaseModel):
    """
    OpenAPI License Object.

    Reference: https://spec.openapis.org/oas/v3.1.0#license-object
    """

    model_config = ConfigDict(extra="allow")

    name: str = Field(..., description="License name (e.g., 'MIT', 'Apache 2.0')")
    identifier: str | None = Field(
        None, description="SPDX license identifier (OAS 3.1.0)"
    )
    url: str | None = None


class InfoObject(BaseModel):
    """
    OpenAPI Info Object.

    Reference: https://spec.openapis.org/oas/v3.1.0#info-object
    """

    model_config = ConfigDict(extra="allow")

    title: str = Field(..., description="API title")
    version: str = Field(..., description="API version (e.g., '1.0.0')")
    summary: str | None = Field(None, description="Short summary (OAS 3.1.0)")
    description: str | None = None
    termsOfService: str | None = None
    contact: ContactObject | None = None
    license: LicenseObject | None = None


class ServerVariableObject(BaseModel):
    """
    OpenAPI Server Variable Object.

    Reference: https://spec.openapis.org/oas/v3.1.0#server-variable-object
    """

    model_config = ConfigDict(extra="allow")

    enum: list[str] | None = None
    default: str = Field(..., description="Default value for substitution")
    description: str | None = None


class ServerObject(BaseModel):
    """
    OpenAPI Server Object.

    Reference: https://spec.openapis.org/oas/v3.1.0#server-object
    """

    model_config = ConfigDict(extra="allow")

    url: str = Field(..., description="Server URL (e.g., 'https://api.example.com')")
    description: str | None = None
    variables: dict[str, ServerVariableObject] | None = None


class ExternalDocumentationObject(BaseModel):
    """
    OpenAPI External Documentation Object.

    Reference: https://spec.openapis.org/oas/v3.1.0#external-documentation-object
    """

    model_config = ConfigDict(extra="allow")

    url: str = Field(..., description="Documentation URL")
    description: str | None = None


class TagObject(BaseModel):
    """
    OpenAPI Tag Object.

    Reference: https://spec.openapis.org/oas/v3.1.0#tag-object
    """

    model_config = ConfigDict(extra="allow")

    name: str = Field(..., description="Tag name")
    description: str | None = None
    externalDocs: ExternalDocumentationObject | None = None


class ReferenceObject(BaseModel):
    """
    OpenAPI Reference Object ($ref).

    Reference: https://spec.openapis.org/oas/v3.1.0#reference-object

    Examples:
        >>> ref = ReferenceObject(ref="#/components/schemas/User")
        >>> ref.ref
        '#/components/schemas/User'
    """

    model_config = ConfigDict(extra="allow")

    ref: str = Field(..., alias="$ref", description="Reference URI")
    summary: str | None = Field(None, description="Summary (OAS 3.1.0)")
    description: str | None = Field(None, description="Description (OAS 3.1.0)")

    @property
    def ref_name(self) -> str:
        """
        Extract referenced name from $ref.

        Examples:
            >>> ReferenceObject(ref="#/components/schemas/User").ref_name
            'User'
            >>> ReferenceObject(ref="#/components/responses/NotFound").ref_name
            'NotFound'
        """
        return self.ref.split("/")[-1]

    @property
    def ref_type(self) -> str:
        """
        Extract reference type from $ref.

        Examples:
            >>> ReferenceObject(ref="#/components/schemas/User").ref_type
            'schemas'
            >>> ReferenceObject(ref="#/components/responses/NotFound").ref_type
            'responses'
        """
        parts = self.ref.split("/")
        if len(parts) >= 3 and parts[1] == "components":
            return parts[2]
        return "unknown"


class ExampleObject(BaseModel):
    """
    OpenAPI Example Object.

    Reference: https://spec.openapis.org/oas/v3.1.0#example-object
    """

    model_config = ConfigDict(extra="allow")

    summary: str | None = None
    description: str | None = None
    value: Any | None = None
    externalValue: str | None = None


class HeaderObject(BaseModel):
    """
    OpenAPI Header Object.

    Reference: https://spec.openapis.org/oas/v3.1.0#header-object
    """

    model_config = ConfigDict(extra="allow")

    description: str | None = None
    required: bool = False
    deprecated: bool = False
    # Schema will be added as SchemaObject | ReferenceObject in schema.py


class LinkObject(BaseModel):
    """
    OpenAPI Link Object.

    Reference: https://spec.openapis.org/oas/v3.1.0#link-object
    """

    model_config = ConfigDict(extra="allow")

    operationRef: str | None = None
    operationId: str | None = None
    parameters: dict[str, Any] | None = None
    requestBody: Any | None = None
    description: str | None = None
    server: ServerObject | None = None
