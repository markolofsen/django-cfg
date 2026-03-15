"""
OpenAPI Input Models - Schema types.

These models represent OpenAPI Schema Objects as they appear in the spec.
Supports both OpenAPI 3.0.3 and 3.1.0 (with JSON Schema extensions).

Reference: https://spec.openapis.org/oas/v3.1.0#schema-object
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from .base import ExternalDocumentationObject, ReferenceObject


class Discriminator(BaseModel):
    """
    OpenAPI Discriminator Object.

    Reference: https://spec.openapis.org/oas/v3.1.0#discriminator-object
    """

    model_config = ConfigDict(extra="allow")

    propertyName: str = Field(..., description="Property name for discrimination")
    mapping: dict[str, str] | None = None


class XMLObject(BaseModel):
    """
    OpenAPI XML Object.

    Reference: https://spec.openapis.org/oas/v3.1.0#xml-object
    """

    model_config = ConfigDict(extra="allow")

    name: str | None = None
    namespace: str | None = None
    prefix: str | None = None
    attribute: bool = False
    wrapped: bool = False


class SchemaObject(BaseModel):
    """
    OpenAPI Schema Object (raw from spec).

    This represents a schema as it appears in the OpenAPI spec, before
    normalization to IR. Supports both OAS 3.0.3 and 3.1.0.

    Key Differences:
    - OAS 3.0.3: Uses nullable: true (proprietary extension)
    - OAS 3.1.0: Uses type: ['string', 'null'] (JSON Schema standard)

    Extensions:
    - x-enum-varnames: drf-spectacular enum variable names
    - x-choices: Django choices metadata

    Reference: https://spec.openapis.org/oas/v3.1.0#schema-object
    """

    model_config = ConfigDict(extra="allow")  # Allow x-* extensions

    # ===== Core JSON Schema Keywords =====
    type: str | list[str] | None = Field(
        None,
        description="JSON Schema type (string, integer, object, array, etc.)",
    )
    format: str | None = Field(
        None,
        description="Format hint (date-time, email, uuid, binary, etc.)",
    )
    title: str | None = None
    description: str | None = None
    default: Any | None = None
    example: Any | None = Field(
        None, description="Example value (deprecated in OAS 3.1.0, use examples)"
    )
    examples: list[Any] | None = Field(
        None, description="Example values (OAS 3.1.0)"
    )

    # ===== Nullable (OAS 3.0.3 only) =====
    nullable: bool | None = Field(
        None,
        description="Can be null (OAS 3.0.3 only, use type: ['x', 'null'] in 3.1.0)",
    )

    # ===== Enum and Const =====
    enum: list[Any] | None = None
    const: Any | None = Field(None, description="Constant value (OAS 3.1.0)")

    # ===== Object Properties =====
    properties: dict[str, SchemaObject | ReferenceObject] | None = None
    required: list[str] | None = None
    additionalProperties: bool | SchemaObject | ReferenceObject | None = None
    maxProperties: int | None = None
    minProperties: int | None = None

    # ===== Array Items =====
    items: SchemaObject | ReferenceObject | None = Field(
        None, description="Array item schema"
    )
    prefixItems: list[SchemaObject | ReferenceObject] | None = Field(
        None, description="Tuple validation (OAS 3.1.0)"
    )
    contains: SchemaObject | ReferenceObject | None = Field(
        None, description="At least one item matches (OAS 3.1.0)"
    )
    maxItems: int | None = None
    minItems: int | None = None
    uniqueItems: bool | None = None

    # ===== String Validation =====
    maxLength: int | None = None
    minLength: int | None = None
    pattern: str | None = None

    # ===== Numeric Validation =====
    maximum: float | None = None
    minimum: float | None = None
    exclusiveMaximum: float | bool | None = Field(
        None, description="Exclusive maximum (number in 3.1.0, boolean in 3.0.3)"
    )
    exclusiveMinimum: float | bool | None = Field(
        None, description="Exclusive minimum (number in 3.1.0, boolean in 3.0.3)"
    )
    multipleOf: float | None = None

    # ===== Composition =====
    allOf: list[SchemaObject | ReferenceObject] | None = None
    oneOf: list[SchemaObject | ReferenceObject] | None = None
    anyOf: list[SchemaObject | ReferenceObject] | None = None
    not_: SchemaObject | ReferenceObject | None = Field(None, alias="not")

    # ===== OpenAPI-Specific =====
    readOnly: bool = False
    writeOnly: bool = False
    deprecated: bool = False
    discriminator: Discriminator | None = None
    xml: XMLObject | None = None
    externalDocs: ExternalDocumentationObject | None = None

    # ===== OAS 3.1.0 Content Metadata =====
    contentMediaType: str | None = Field(
        None, description="Media type (OAS 3.1.0, e.g., 'application/json')"
    )
    contentEncoding: str | None = Field(
        None, description="Encoding (OAS 3.1.0, e.g., 'base64')"
    )
    contentSchema: SchemaObject | ReferenceObject | None = Field(
        None, description="Schema for content (OAS 3.1.0)"
    )

    # ===== Django/drf-spectacular Extensions =====
    x_enum_varnames: list[str] | None = Field(
        None,
        alias="x-enum-varnames",
        description="Enum variable names from drf-spectacular",
    )
    x_spec_enum_id: str | None = Field(
        None,
        alias="x-spec-enum-id",
        description="Unique enum identifier from drf-spectacular (same ID = same enum)",
    )
    x_choices: list[dict[str, Any]] | None = Field(
        None,
        alias="x-choices",
        description="Django choices from drf-spectacular",
    )

    @property
    def is_nullable_30(self) -> bool:
        """Check if nullable via OAS 3.0.3 style (nullable: true)."""
        return self.nullable is True

    @property
    def is_nullable_31(self) -> bool:
        """
        Check if nullable via OAS 3.1.0 style (type: ['string', 'null']).

        Examples:
            >>> schema = SchemaObject(type=['string', 'null'])
            >>> schema.is_nullable_31
            True

            >>> schema = SchemaObject(type='string')
            >>> schema.is_nullable_31
            False
        """
        if isinstance(self.type, list):
            return "null" in self.type
        return False

    @property
    def base_type(self) -> str | None:
        """
        Get base type (excluding 'null').

        For OAS 3.1.0 type: ['string', 'null'], returns 'string'.

        Examples:
            >>> SchemaObject(type='string').base_type
            'string'
            >>> SchemaObject(type=['string', 'null']).base_type
            'string'
            >>> SchemaObject(type=['integer', 'null']).base_type
            'integer'
        """
        if isinstance(self.type, list):
            types = [t for t in self.type if t != "null"]
            return types[0] if types else None
        return self.type

    @property
    def has_enum_varnames(self) -> bool:
        """Check if x-enum-varnames extension is present."""
        return (
            self.enum is not None
            and self.x_enum_varnames is not None
            and len(self.enum) == len(self.x_enum_varnames)
        )

    @property
    def is_object(self) -> bool:
        """Check if schema is object type."""
        return self.base_type == "object" or self.properties is not None

    @property
    def is_array(self) -> bool:
        """Check if schema is array type."""
        return self.base_type == "array" or self.items is not None

    @property
    def is_primitive(self) -> bool:
        """Check if schema is primitive type."""
        return self.base_type in ("string", "integer", "number", "boolean")

    @property
    def is_binary(self) -> bool:
        """
        Check if schema represents binary data.

        Handles both OAS 3.0.3 (format: binary) and OAS 3.1.0 (contentEncoding).
        """
        return self.format == "binary" or self.contentEncoding in ("base64", "binary")

    def __repr__(self) -> str:
        """String representation for debugging."""
        parts = ["SchemaObject("]

        if self.type:
            parts.append(f"type={self.type!r}")

        if self.format:
            parts.append(f"format={self.format!r}")

        if self.nullable:
            parts.append("nullable=True")

        if self.enum:
            parts.append(f"enum={self.enum}")

        if self.x_enum_varnames:
            parts.append(f"x-enum-varnames={self.x_enum_varnames}")

        return ", ".join(parts) + ")"
