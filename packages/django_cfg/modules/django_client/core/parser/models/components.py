"""
OpenAPI Input Models - Components Object.

ComponentsObject holds reusable schemas, responses, parameters, etc.

Reference: https://spec.openapis.org/oas/v3.1.0#components-object
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from .base import ExampleObject, LinkObject, ReferenceObject
from .operation import (
    CallbackObject,
    ParameterObject,
    RequestBodyObject,
    ResponseObject,
)
from .schema import SchemaObject


class SecuritySchemeObject(BaseModel):
    """
    OpenAPI Security Scheme Object.

    Reference: https://spec.openapis.org/oas/v3.1.0#security-scheme-object
    """

    model_config = ConfigDict(extra="allow")

    type: str = Field(
        ...,
        description="Security type: apiKey, http, oauth2, openIdConnect",
    )
    description: str | None = None

    # apiKey
    name: str | None = Field(None, description="Header/query/cookie name (for apiKey)")
    in_: str | None = Field(None, alias="in", description="Location: query, header, cookie")

    # http
    scheme: str | None = Field(None, description="HTTP scheme: basic, bearer, etc.")
    bearerFormat: str | None = None

    # oauth2
    flows: dict[str, Any] | None = None  # OAuthFlowsObject

    # openIdConnect
    openIdConnectUrl: str | None = None


class ComponentsObject(BaseModel):
    """
    OpenAPI Components Object.

    Contains reusable schemas, responses, parameters, etc.

    Reference: https://spec.openapis.org/oas/v3.1.0#components-object
    """

    model_config = ConfigDict(extra="allow")

    # ===== Schemas (most important for us) =====
    schemas: dict[str, SchemaObject | ReferenceObject] | None = Field(
        None,
        description="Reusable schemas (User, UserRequest, PatchedUser, etc.)",
    )

    # ===== Responses =====
    responses: dict[str, ResponseObject | ReferenceObject] | None = Field(
        None,
        description="Reusable responses (NotFound, ValidationError, etc.)",
    )

    # ===== Parameters =====
    parameters: dict[str, ParameterObject | ReferenceObject] | None = Field(
        None,
        description="Reusable parameters",
    )

    # ===== Examples =====
    examples: dict[str, ExampleObject | ReferenceObject] | None = Field(
        None,
        description="Reusable examples",
    )

    # ===== Request Bodies =====
    requestBodies: dict[str, RequestBodyObject | ReferenceObject] | None = Field(
        None,
        description="Reusable request bodies",
    )

    # ===== Headers =====
    headers: dict[str, Any] | None = Field(
        None,
        description="Reusable headers (HeaderObject | ReferenceObject)",
    )

    # ===== Security Schemes =====
    securitySchemes: dict[str, SecuritySchemeObject | ReferenceObject] | None = Field(
        None,
        description="Security schemes (basicAuth, bearerAuth, etc.)",
    )

    # ===== Links =====
    links: dict[str, LinkObject | ReferenceObject] | None = Field(
        None,
        description="Reusable links",
    )

    # ===== Callbacks =====
    callbacks: dict[str, CallbackObject | ReferenceObject] | None = Field(
        None,
        description="Reusable callbacks",
    )

    # ===== Path Items (OAS 3.1.0) =====
    pathItems: dict[str, Any] | None = Field(
        None,
        description="Reusable path items (OAS 3.1.0)",
    )

    @property
    def has_schemas(self) -> bool:
        """Check if components contain schemas."""
        return self.schemas is not None and len(self.schemas) > 0

    @property
    def schema_names(self) -> list[str]:
        """Get all schema names."""
        if not self.schemas:
            return []
        return list(self.schemas.keys())

    def get_schema(self, name: str) -> SchemaObject | ReferenceObject | None:
        """Get schema by name."""
        if not self.schemas:
            return None
        return self.schemas.get(name)

    def __repr__(self) -> str:
        """String representation for debugging."""
        parts = ["ComponentsObject("]

        if self.schemas:
            parts.append(f"schemas={len(self.schemas)}")

        if self.responses:
            parts.append(f"responses={len(self.responses)}")

        if self.parameters:
            parts.append(f"parameters={len(self.parameters)}")

        if self.securitySchemes:
            parts.append(f"securitySchemes={len(self.securitySchemes)}")

        return ", ".join(parts) + ")"
