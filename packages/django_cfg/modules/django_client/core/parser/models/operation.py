"""
OpenAPI Input Models - Operation types.

These models represent OpenAPI operations (endpoints) as they appear in the spec.

Reference: https://spec.openapis.org/oas/v3.1.0
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from .base import ExampleObject, ExternalDocumentationObject, ReferenceObject, ServerObject
from .schema import SchemaObject


class ParameterObject(BaseModel):
    """
    OpenAPI Parameter Object.

    Reference: https://spec.openapis.org/oas/v3.1.0#parameter-object
    """

    model_config = ConfigDict(extra="allow")

    name: str = Field(..., description="Parameter name")
    in_: Literal["query", "header", "path", "cookie"] = Field(
        ..., alias="in", description="Parameter location"
    )
    description: str | None = None
    required: bool = False
    deprecated: bool = False
    allowEmptyValue: bool = False

    # Schema (simplified - can also use content for complex types)
    schema_: SchemaObject | ReferenceObject | None = Field(None, alias="schema")

    # Style and explode (for serialization)
    style: str | None = None
    explode: bool | None = None
    allowReserved: bool = False

    # Example
    example: Any | None = None
    examples: dict[str, ExampleObject | ReferenceObject] | None = None


class EncodingObject(BaseModel):
    """
    OpenAPI Encoding Object.

    Reference: https://spec.openapis.org/oas/v3.1.0#encoding-object
    """

    model_config = ConfigDict(extra="allow")

    contentType: str | None = None
    headers: dict[str, Any] | None = None  # HeaderObject | ReferenceObject
    style: str | None = None
    explode: bool | None = None
    allowReserved: bool = False


class MediaTypeObject(BaseModel):
    """
    OpenAPI Media Type Object.

    Reference: https://spec.openapis.org/oas/v3.1.0#media-type-object
    """

    model_config = ConfigDict(extra="allow")

    schema_: SchemaObject | ReferenceObject | None = Field(None, alias="schema")
    example: Any | None = None
    examples: dict[str, ExampleObject | ReferenceObject] | None = None
    encoding: dict[str, EncodingObject] | None = None


class RequestBodyObject(BaseModel):
    """
    OpenAPI Request Body Object.

    Reference: https://spec.openapis.org/oas/v3.1.0#request-body-object
    """

    model_config = ConfigDict(extra="allow")

    description: str | None = None
    content: dict[str, MediaTypeObject] = Field(
        ..., description="Content by media type (application/json, etc.)"
    )
    required: bool = False


class ResponseObject(BaseModel):
    """
    OpenAPI Response Object.

    Reference: https://spec.openapis.org/oas/v3.1.0#response-object
    """

    model_config = ConfigDict(extra="allow")

    description: str = Field(..., description="Response description")
    headers: dict[str, Any] | None = None  # HeaderObject | ReferenceObject
    content: dict[str, MediaTypeObject] | None = None
    links: dict[str, Any] | None = None  # LinkObject | ReferenceObject


class CallbackObject(BaseModel):
    """
    OpenAPI Callback Object.

    Reference: https://spec.openapis.org/oas/v3.1.0#callback-object
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    # Callbacks are PathItemObjects keyed by expression
    # We'll keep it simple as dict for now


class OperationObject(BaseModel):
    """
    OpenAPI Operation Object.

    Reference: https://spec.openapis.org/oas/v3.1.0#operation-object
    """

    model_config = ConfigDict(extra="allow")

    # Identification
    operationId: str | None = None
    summary: str | None = None
    description: str | None = None
    tags: list[str] | None = None

    # External docs
    externalDocs: ExternalDocumentationObject | None = None

    # Parameters
    parameters: list[ParameterObject | ReferenceObject] | None = None

    # Request body
    requestBody: RequestBodyObject | ReferenceObject | None = None

    # Responses
    responses: dict[str, ResponseObject | ReferenceObject] = Field(
        ..., description="Responses by status code ('200', '404', 'default', etc.)"
    )

    # Callbacks
    callbacks: dict[str, CallbackObject | ReferenceObject] | None = None

    # Security
    security: list[dict[str, list[str]]] | None = None

    # Servers
    servers: list[ServerObject] | None = None

    # Deprecation
    deprecated: bool = False


class PathItemObject(BaseModel):
    """
    OpenAPI Path Item Object.

    Reference: https://spec.openapis.org/oas/v3.1.0#path-item-object
    """

    model_config = ConfigDict(extra="allow")

    # Reference (allows $ref at path level)
    ref: str | None = Field(None, alias="$ref")

    # Summary and description
    summary: str | None = None
    description: str | None = None

    # Operations
    get: OperationObject | None = None
    put: OperationObject | None = None
    post: OperationObject | None = None
    delete: OperationObject | None = None
    options: OperationObject | None = None
    head: OperationObject | None = None
    patch: OperationObject | None = None
    trace: OperationObject | None = None

    # Servers
    servers: list[ServerObject] | None = None

    # Parameters (apply to all operations)
    parameters: list[ParameterObject | ReferenceObject] | None = None

    @property
    def operations(self) -> dict[str, OperationObject]:
        """Get all operations in this path."""
        result = {}
        for method in ("get", "post", "put", "patch", "delete", "head", "options", "trace"):
            operation = getattr(self, method, None)
            if operation:
                result[method.upper()] = operation
        return result
