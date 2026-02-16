"""
Field Context Builder.

Pre-computes all values needed by templates from IRSchemaObject + Smart Detection.
This centralizes logic that was previously scattered across generators and templates.

Usage:
    from django_cfg.modules.django_client.core.context import build_field_context, build_schema_context
    from django_cfg.modules.django_client.core.ir import IRSchemaObject

    # Single field
    field = IRSchemaObject(name="email", type="string")
    ctx = build_field_context(field, required=True)
    # ctx.ts_type == "string"
    # ctx.input_type == "email"
    # ctx.validation == "email"

    # Full schema with all fields
    schema = IRSchemaObject(name="User", type="object", properties={...})
    schema_ctx = build_schema_context(schema)
    # schema_ctx.fields == [FieldContext(...), ...]
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from ..detection import detect_field_meta, InputType, ValidationRule
from ..types import FieldType, FormatType, TypeMapper

if TYPE_CHECKING:
    from ..ir import IRSchemaObject


@dataclass(frozen=True, slots=True)
class FieldContext:
    """
    Pre-computed field context for templates.

    Contains all values a template might need, computed once in Python
    rather than in Jinja2 templates.
    """

    # === Identity ===
    name: str
    original_name: str  # Before any sanitization

    # === Types (pre-computed for each language) ===
    python_type: str
    ts_type: str
    zod_type: str
    go_type: str
    proto_type: str

    # === OpenAPI metadata ===
    field_type: FieldType
    format_type: FormatType | None
    description: str | None
    example: Any | None
    default: Any | None

    # === Required/Optional/Nullable ===
    required: bool
    nullable: bool
    optional: bool  # Computed: not required or nullable

    # === Read/Write ===
    read_only: bool
    write_only: bool
    readonly: bool  # Merged: read_only OR detected as readonly (timestamps, ids)

    # === Smart Detection ===
    input_type: InputType
    validation: ValidationRule | None
    sensitive: bool
    placeholder: str | None
    autocomplete: str | None
    pattern: str | None

    # === Validation constraints from OpenAPI ===
    min_length: int | None
    max_length: int | None
    minimum: float | None
    maximum: float | None
    exclusive_minimum: float | None
    exclusive_maximum: float | None
    multiple_of: float | None

    # === Computed flags ===
    has_validation: bool  # Has any validation constraints
    is_array: bool
    is_object: bool
    is_enum: bool
    is_binary: bool
    is_ref: bool  # References another schema

    # === Reference info ===
    ref: str | None  # $ref target if is_ref

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for template context."""
        return {
            # Identity
            "name": self.name,
            "original_name": self.original_name,
            # Types
            "python_type": self.python_type,
            "ts_type": self.ts_type,
            "zod_type": self.zod_type,
            "go_type": self.go_type,
            "proto_type": self.proto_type,
            # OpenAPI
            "field_type": self.field_type.value,
            "format_type": self.format_type.value if self.format_type else None,
            "description": self.description,
            "example": self.example,
            "default": self.default,
            # Required/Optional
            "required": self.required,
            "nullable": self.nullable,
            "optional": self.optional,
            # Read/Write
            "read_only": self.read_only,
            "write_only": self.write_only,
            "readonly": self.readonly,
            # Smart Detection
            "input_type": self.input_type.value,
            "validation": self.validation.value if self.validation else None,
            "sensitive": self.sensitive,
            "placeholder": self.placeholder,
            "autocomplete": self.autocomplete,
            "pattern": self.pattern,
            # Validation
            "min_length": self.min_length,
            "max_length": self.max_length,
            "minimum": self.minimum,
            "maximum": self.maximum,
            "has_validation": self.has_validation,
            # Flags
            "is_array": self.is_array,
            "is_object": self.is_object,
            "is_enum": self.is_enum,
            "is_binary": self.is_binary,
            "is_ref": self.is_ref,
            "ref": self.ref,
        }


@dataclass(frozen=True, slots=True)
class SchemaContext:
    """
    Pre-computed schema context for templates.

    Contains the schema itself plus all fields as FieldContext.
    """

    # === Identity ===
    name: str
    description: str | None

    # === Model type ===
    is_request_model: bool
    is_response_model: bool
    is_patch_model: bool

    # === Fields ===
    fields: tuple[FieldContext, ...]
    required_fields: tuple[str, ...]

    # === Computed ===
    has_required_fields: bool
    has_optional_fields: bool
    has_sensitive_fields: bool
    has_readonly_fields: bool
    field_count: int

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for template context."""
        return {
            "name": self.name,
            "description": self.description,
            "is_request_model": self.is_request_model,
            "is_response_model": self.is_response_model,
            "is_patch_model": self.is_patch_model,
            "fields": [f.to_dict() for f in self.fields],
            "required_fields": list(self.required_fields),
            "has_required_fields": self.has_required_fields,
            "has_optional_fields": self.has_optional_fields,
            "has_sensitive_fields": self.has_sensitive_fields,
            "has_readonly_fields": self.has_readonly_fields,
            "field_count": self.field_count,
        }


def build_field_context(
    schema: IRSchemaObject,
    *,
    required: bool = True,
) -> FieldContext:
    """
    Build comprehensive field context from IRSchemaObject.

    Args:
        schema: IR schema object for the field
        required: Whether field is required in parent schema

    Returns:
        FieldContext with all pre-computed values
    """
    mapper = TypeMapper()

    # Determine field type
    try:
        ft = FieldType(schema.type)
    except ValueError:
        ft = FieldType.ANY

    # Determine format type
    fmt: FormatType | None = None
    if schema.format:
        try:
            fmt = FormatType(schema.format)
        except ValueError:
            pass

    # Get smart detection metadata
    meta = detect_field_meta(
        schema.name,
        ft,
        format_type=fmt,
        read_only=schema.read_only,
        write_only=schema.write_only,
    )

    # Compute types for each language
    python_type = schema.python_type
    ts_type = schema.typescript_type
    zod_type = mapper.to_zod(ft, fmt, nullable=schema.nullable, optional=not required)
    go_type = mapper.to_go(ft, fmt, optional=not required)
    proto_type = mapper.to_proto(ft, fmt)

    # Compute flags
    is_optional = not required or schema.nullable
    readonly = schema.read_only or meta.readonly
    has_validation = bool(
        schema.min_length
        or schema.max_length
        or schema.pattern
        or schema.minimum
        or schema.maximum
        or meta.validation
    )

    return FieldContext(
        # Identity
        name=schema.name,
        original_name=schema.name,
        # Types
        python_type=python_type,
        ts_type=ts_type,
        zod_type=zod_type,
        go_type=go_type,
        proto_type=proto_type,
        # OpenAPI
        field_type=ft,
        format_type=fmt,
        description=schema.description,
        example=schema.example,
        default=schema.default,
        # Required/Optional
        required=required,
        nullable=schema.nullable,
        optional=is_optional,
        # Read/Write
        read_only=schema.read_only,
        write_only=schema.write_only,
        readonly=readonly,
        # Smart Detection
        input_type=meta.input_type,
        validation=meta.validation,
        sensitive=meta.sensitive,
        placeholder=meta.placeholder,
        autocomplete=meta.autocomplete,
        pattern=meta.pattern or schema.pattern,
        # Validation
        min_length=schema.min_length,
        max_length=schema.max_length,
        minimum=schema.minimum,
        maximum=schema.maximum,
        exclusive_minimum=schema.exclusive_minimum,
        exclusive_maximum=schema.exclusive_maximum,
        multiple_of=schema.multiple_of,
        # Computed
        has_validation=has_validation,
        is_array=schema.is_array,
        is_object=schema.is_object,
        is_enum=schema.has_enum,
        is_binary=schema.is_binary,
        is_ref=schema.ref is not None,
        ref=schema.ref,
    )


def build_schema_context(schema: IRSchemaObject) -> SchemaContext:
    """
    Build comprehensive schema context with all fields.

    Args:
        schema: IR schema object (type=object with properties)

    Returns:
        SchemaContext with all fields as FieldContext
    """
    required_set = set(schema.required or [])

    # Build field contexts
    fields: list[FieldContext] = []
    for prop_name, prop_schema in (schema.properties or {}).items():
        is_required = prop_name in required_set
        field_ctx = build_field_context(prop_schema, required=is_required)
        fields.append(field_ctx)

    # Compute aggregates
    has_required = any(f.required for f in fields)
    has_optional = any(f.optional for f in fields)
    has_sensitive = any(f.sensitive for f in fields)
    has_readonly = any(f.readonly for f in fields)

    return SchemaContext(
        name=schema.name,
        description=schema.description,
        is_request_model=schema.is_request_model,
        is_response_model=schema.is_response_model,
        is_patch_model=schema.is_patch_model,
        fields=tuple(fields),
        required_fields=tuple(schema.required or []),
        has_required_fields=has_required,
        has_optional_fields=has_optional,
        has_sensitive_fields=has_sensitive,
        has_readonly_fields=has_readonly,
        field_count=len(fields),
    )
