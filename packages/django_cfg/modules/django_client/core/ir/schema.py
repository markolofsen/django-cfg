"""
IR Schema Models - Type-safe schema representation with Request/Response split.

This module defines the intermediate representation for OpenAPI schemas,
normalized from both OpenAPI 3.0.3 and 3.1.0.

Key Features:
- Request/Response split detection (UserRequest vs User)
- x-enum-varnames support for strongly typed enums
- Nullable normalization (3.0 nullable: true vs 3.1 type: [.., 'null'])
- 100% Pydantic 2 with strict validation
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class IRSchemaObject(BaseModel):
    """
    Unified schema representation (version-agnostic, language-agnostic).

    This model represents a single schema component from the OpenAPI spec,
    normalized for both OpenAPI 3.0.3 and 3.1.0.

    Key Features:
    - Request/Response awareness: Detects UserRequest vs User patterns
    - x-enum-varnames: Strongly typed enums from drf-spectacular
    - Nullable normalization: Both 3.0 and 3.1 → single `nullable` field

    Examples:
        >>> # Response model
        >>> user_response = IRSchemaObject(
        ...     name="User",
        ...     type="object",
        ...     properties={
        ...         "id": IRSchemaObject(name="id", type="integer"),
        ...         "username": IRSchemaObject(name="username", type="string"),
        ...     },
        ...     required=["id", "username"],
        ...     is_request_model=False,
        ... )

        >>> # Request model (no readOnly fields)
        >>> user_request = IRSchemaObject(
        ...     name="UserRequest",
        ...     type="object",
        ...     properties={
        ...         "username": IRSchemaObject(name="username", type="string"),
        ...         "email": IRSchemaObject(name="email", type="string"),
        ...     },
        ...     required=["username", "email"],
        ...     is_request_model=True,
        ...     related_response="User",
        ... )

        >>> # Enum with x-enum-varnames
        >>> status_enum = IRSchemaObject(
        ...     name="status",
        ...     type="integer",
        ...     enum=[1, 2, 3],
        ...     enum_var_names=["STATUS_NEW", "STATUS_IN_PROGRESS", "STATUS_COMPLETE"],
        ... )
        >>> assert status_enum.has_enum is True
    """

    model_config = ConfigDict(
        validate_assignment=True,  # Validate on attribute assignment
        extra="forbid",  # No extra fields allowed
        frozen=False,  # Allow mutations (for plugin transforms)
        validate_default=True,  # Validate default values
        str_strip_whitespace=True,  # Strip whitespace from strings
    )

    # ===== Core Fields =====
    name: str = Field(..., description="Schema name (e.g., 'User', 'UserRequest')")
    type: str = Field(
        ...,
        description="JSON Schema type: object, string, integer, number, boolean, array, null",
    )
    format: str | None = Field(
        None,
        description="Format hint: date-time, email, uri, uuid, binary, etc.",
    )
    description: str | None = Field(
        None, description="Human-readable description"
    )

    # ===== Nullable (Normalized from 3.0 and 3.1) =====
    nullable: bool = Field(
        False,
        description="Can be null (normalized from OAS 3.0 nullable: true or 3.1 type: ['string', 'null'])",
    )

    # ===== Object Properties =====
    properties: dict[str, IRSchemaObject] = Field(
        default_factory=dict,
        description="Object properties (for type: object)",
    )
    required: list[str] = Field(
        default_factory=list,
        description="Required property names",
    )
    additional_properties: IRSchemaObject | None = Field(
        None,
        description="Schema for additional properties (for dynamic keys in object, e.g., Record<string, T>)",
    )

    # ===== Array Items =====
    items: IRSchemaObject | None = Field(
        None,
        description="Array item schema (for type: array)",
    )

    # ===== Enum Support (with x-enum-varnames) =====
    enum: list[str | int | float] | None = Field(
        None,
        description="Enum values (e.g., [1, 2, 3] or ['active', 'inactive'])",
    )
    enum_var_names: list[str] | None = Field(
        None,
        description="Enum variable names from x-enum-varnames (e.g., ['STATUS_NEW', 'STATUS_IN_PROGRESS'])",
    )
    choices: list[dict[str, Any]] | None = Field(
        None,
        description="Django choices from x-choices (e.g., [{'value': 1, 'display_name': 'Active'}])",
    )
    const: str | int | float | None = Field(
        None,
        description="Constant value (OAS 3.1 const keyword)",
    )

    # ===== Validation Constraints =====
    min_length: int | None = Field(None, ge=0, description="Minimum string length")
    max_length: int | None = Field(None, ge=0, description="Maximum string length")
    pattern: str | None = Field(None, description="Regex pattern for string validation")
    minimum: int | float | None = Field(None, description="Minimum numeric value")
    maximum: int | float | None = Field(None, description="Maximum numeric value")
    exclusive_minimum: int | float | None = Field(
        None, description="Exclusive minimum"
    )
    exclusive_maximum: int | float | None = Field(
        None, description="Exclusive maximum"
    )
    multiple_of: int | float | None = Field(None, gt=0, description="Multiple of")

    # ===== References =====
    ref: str | None = Field(
        None,
        description="$ref reference (e.g., '#/components/schemas/Profile')",
    )

    # ===== Request/Response Split (NEW) =====
    is_request_model: bool = Field(
        False,
        description="True if this is a request model (UserRequest, PatchedUser)",
    )
    is_response_model: bool = Field(
        True,
        description="True if this is a response model (User - default)",
    )
    related_request: str | None = Field(
        None,
        description="Related request model name (User → UserRequest)",
    )
    related_response: str | None = Field(
        None,
        description="Related response model name (UserRequest → User)",
    )
    is_patch_model: bool = Field(
        False,
        description="True if this is a PATCH model (PatchedUser)",
    )

    # ===== Content Metadata (OAS 3.1) =====
    content_media_type: str | None = Field(
        None,
        description="Content media type (OAS 3.1 contentMediaType)",
    )
    content_encoding: str | None = Field(
        None,
        description="Content encoding (OAS 3.1 contentEncoding, e.g., 'base64')",
    )

    # ===== Additional Metadata =====
    read_only: bool = Field(
        False,
        description="Field is read-only (appears in responses only)",
    )
    write_only: bool = Field(
        False,
        description="Field is write-only (appears in requests only)",
    )
    deprecated: bool = Field(False, description="Field is deprecated")
    example: Any | None = Field(None, description="Example value")
    default: Any | None = Field(
        None,
        description="Default value (used to infer array vs object for JSONField)",
    )

    # ===== Computed Properties =====

    @property
    def has_enum(self) -> bool:
        """
        Check if this field is an enum with variable names.

        Returns:
            True if enum and enum_var_names are both present.

        Examples:
            >>> schema = IRSchemaObject(
            ...     name="status",
            ...     type="integer",
            ...     enum=[1, 2, 3],
            ...     enum_var_names=["STATUS_NEW", "STATUS_IN_PROGRESS", "STATUS_COMPLETE"],
            ... )
            >>> schema.has_enum
            True

            >>> schema_no_names = IRSchemaObject(
            ...     name="status",
            ...     type="integer",
            ...     enum=[1, 2, 3],
            ... )
            >>> schema_no_names.has_enum
            False
        """
        return (
            self.enum is not None
            and self.enum_var_names is not None
            and len(self.enum) == len(self.enum_var_names)
        )

    @property
    def is_object(self) -> bool:
        """Check if type is object."""
        return self.type == "object"

    @property
    def is_array(self) -> bool:
        """Check if type is array."""
        return self.type == "array"

    @property
    def is_primitive(self) -> bool:
        """Check if type is primitive (string, integer, number, boolean)."""
        return self.type in ("string", "integer", "number", "boolean")

    @property
    def is_binary(self) -> bool:
        """
        Check if field represents binary data.

        Handles both OAS 3.0 (format: binary) and OAS 3.1 (contentEncoding: base64).

        Returns:
            True if field is binary.
        """
        return self.format == "binary" or self.content_encoding == "base64"

    @property
    def python_type(self) -> str:
        """
        Get Python type hint for this schema.

        Returns:
            Python type as string (e.g., "str", "int", "list[str]").

        Examples:
            >>> IRSchemaObject(name="x", type="string").python_type
            'str'
            >>> IRSchemaObject(name="x", type="integer").python_type
            'int'
            >>> IRSchemaObject(name="x", type="string", nullable=True).python_type
            'str | None'
            >>> IRSchemaObject(name="x", type="string", read_only=True).python_type
            'Any'
            >>> IRSchemaObject(name="x", type="object", default=[]).python_type
            'list[Any]'
        """
        # For read-only string fields, use Any since they often return complex objects
        # from SerializerMethodField in Django (e.g., dicts instead of strings)
        if self.read_only and self.type == "string":
            return "Any | None" if self.nullable else "Any"

        # SMART DETECTION: JSONField(default=list) case
        # When type=object but default=[], it's actually an array
        if self.type == "object" and not self.properties:
            # Check if default value is a list
            if isinstance(self.default, list):
                return "list[Any] | None" if self.nullable else "list[Any]"
            # Otherwise treat as dict with any values
            # SAFETY: Always use Any for values to handle DictField edge cases
            return "dict[str, Any] | None" if self.nullable else "dict[str, Any]"

        type_map = {
            "string": "str",
            "integer": "int",
            "number": "float",
            "boolean": "bool",
            "array": f"list[{self.items.python_type if self.items else 'Any'}]",
            "object": "dict[str, Any]",
        }

        base_type = type_map.get(self.type, "Any")

        if self.nullable:
            return f"{base_type} | None"

        return base_type

    @property
    def typescript_type(self) -> str:
        """
        Get TypeScript type for this schema.

        Returns:
            TypeScript type as string (e.g., "string", "number", "Array<string>").

        Examples:
            >>> IRSchemaObject(name="x", type="string").typescript_type
            'string'
            >>> IRSchemaObject(name="x", type="integer").typescript_type
            'number'
            >>> IRSchemaObject(name="x", type="string", nullable=True).typescript_type
            'string | null'
            >>> # Array with $ref items
            >>> IRSchemaObject(
            ...     name="users",
            ...     type="array",
            ...     items=IRSchemaObject(name="User", type="object", ref="User")
            ... ).typescript_type
            'Array<User>'
            >>> # Binary field (file upload)
            >>> IRSchemaObject(name="file", type="string", format="binary").typescript_type
            'File | Blob'
        """
        # Handle $ref (e.g., CentrifugoConfig, User, etc.)
        if self.ref:
            base_type = self.ref
        # Handle binary type (file uploads)
        elif self.is_binary:
            base_type = "File | Blob"
        # Handle array type with proper item type resolution
        elif self.type == "array":
            if self.items:
                # If items is a $ref, use the ref name directly
                if self.items.ref:
                    item_type = self.items.ref
                else:
                    item_type = self.items.typescript_type
                base_type = f"Array<{item_type}>"
            else:
                base_type = "Array<any>"
        # Handle object with additionalProperties (e.g., Record<string, DatabaseConfig>)
        elif self.type == "object" and self.additional_properties:
            # SMART DETECTION: Check if default=[] for JSONField(default=list)
            if isinstance(self.default, list):
                base_type = "Array<any>"
            elif self.additional_properties.ref:
                # Only trust $ref types (explicit nested serializers)
                value_type = self.additional_properties.ref
                base_type = f"Record<string, {value_type}>"
            else:
                # SAFETY: Always use 'any' for additionalProperties without $ref
                # DictField generates additionalProperties: {type: string} which is too restrictive
                # Real data often contains boolean, number, nested objects
                base_type = "Record<string, any>"
        # Handle plain object without properties
        elif self.type == "object" and not self.properties:
            # SMART DETECTION: JSONField(default=list) case
            if isinstance(self.default, list):
                base_type = "Array<any>"
            else:
                base_type = "Record<string, any>"
        else:
            type_map = {
                "string": "string",
                "integer": "number",
                "number": "number",
                "boolean": "boolean",
                "object": "Record<string, any>",
                "any": "any",
            }
            base_type = type_map.get(self.type, "any")

        if self.nullable:
            return f"{base_type} | null"

        return base_type

    def __repr__(self) -> str:
        """String representation for debugging."""
        parts = [f"IRSchemaObject(name={self.name!r}", f"type={self.type!r}"]

        if self.nullable:
            parts.append("nullable=True")

        if self.is_request_model:
            parts.append("is_request_model=True")

        if self.has_enum:
            parts.append(f"enum={self.enum}")

        if self.ref:
            parts.append(f"ref={self.ref!r}")

        return ", ".join(parts) + ")"
