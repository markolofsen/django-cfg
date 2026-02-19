"""
Unified Field Type System.

Single source of truth for type mappings across all target languages.
This eliminates duplication between IRSchemaObject, GoTypeMapper, ProtoTypeMapper, etc.

Usage:
    from django_cfg.modules.django_client.core.types import FieldType, TypeMapper

    # Get type for any language
    mapper = TypeMapper()
    mapper.to_python(FieldType.STRING)  # "str"
    mapper.to_typescript(FieldType.STRING)  # "string"
    mapper.to_zod(FieldType.STRING)  # "z.string()"
    mapper.to_go(FieldType.STRING)  # "string"

    # With format
    mapper.to_python(FieldType.STRING, FormatType.DATETIME)  # "datetime"
    mapper.to_typescript(FieldType.STRING, FormatType.DATETIME)  # "string"
    mapper.to_go(FieldType.STRING, FormatType.DATETIME)  # "time.Time"
"""

from __future__ import annotations

from enum import Enum
from typing import NamedTuple


class FieldType(str, Enum):
    """OpenAPI/JSON Schema field types."""

    STRING = "string"
    INTEGER = "integer"
    NUMBER = "number"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"
    NULL = "null"
    ANY = "any"


class FormatType(str, Enum):
    """OpenAPI format specifiers."""

    # String formats
    DATETIME = "date-time"
    DATE = "date"
    TIME = "time"
    UUID = "uuid"
    EMAIL = "email"
    URI = "uri"
    URL = "url"
    HOSTNAME = "hostname"
    IPV4 = "ipv4"
    IPV6 = "ipv6"
    PASSWORD = "password"
    BINARY = "binary"
    BYTE = "byte"

    # Integer formats
    INT32 = "int32"
    INT64 = "int64"

    # Number formats
    FLOAT = "float"
    DOUBLE = "double"


# =============================================================================
# Python Type Mappings
# =============================================================================

PYTHON_TYPES: dict[FieldType, str] = {
    FieldType.STRING: "str",
    FieldType.INTEGER: "int",
    FieldType.NUMBER: "float",
    FieldType.BOOLEAN: "bool",
    FieldType.ARRAY: "list",
    FieldType.OBJECT: "dict[str, Any]",
    FieldType.NULL: "None",
    FieldType.ANY: "Any",
}

PYTHON_FORMAT_TYPES: dict[FormatType, str] = {
    FormatType.DATETIME: "datetime.datetime",
    FormatType.DATE: "datetime.date",
    FormatType.TIME: "datetime.time",
    FormatType.UUID: "str",  # Could use UUID but str is simpler
    FormatType.EMAIL: "str",
    FormatType.URI: "str",
    FormatType.URL: "str",
    FormatType.HOSTNAME: "str",
    FormatType.IPV4: "str",
    FormatType.IPV6: "str",
    FormatType.PASSWORD: "str",
    FormatType.BINARY: "Any",  # Accept file-like objects
    FormatType.BYTE: "bytes",
    FormatType.INT32: "int",
    FormatType.INT64: "int",
    FormatType.FLOAT: "float",
    FormatType.DOUBLE: "float",
}

# Python imports needed for specific types
PYTHON_IMPORTS: dict[str, str] = {
    "datetime.datetime": "import datetime",
    "datetime.date": "import datetime",
    "datetime.time": "import datetime",
    "datetime": "import datetime",  # fallback for old references
    "date": "import datetime",  # fallback for old references
    "time": "import datetime",  # fallback for old references
    "Any": "from typing import Any",
    "UUID": "from uuid import UUID",
}


# =============================================================================
# TypeScript Type Mappings
# =============================================================================

TYPESCRIPT_TYPES: dict[FieldType, str] = {
    FieldType.STRING: "string",
    FieldType.INTEGER: "number",
    FieldType.NUMBER: "number",
    FieldType.BOOLEAN: "boolean",
    FieldType.ARRAY: "Array<any>",
    FieldType.OBJECT: "Record<string, any>",
    FieldType.NULL: "null",
    FieldType.ANY: "any",
}

TYPESCRIPT_FORMAT_TYPES: dict[FormatType, str] = {
    FormatType.DATETIME: "string",  # ISO 8601 string
    FormatType.DATE: "string",
    FormatType.TIME: "string",
    FormatType.UUID: "string",
    FormatType.EMAIL: "string",
    FormatType.URI: "string",
    FormatType.URL: "string",
    FormatType.HOSTNAME: "string",
    FormatType.IPV4: "string",
    FormatType.IPV6: "string",
    FormatType.PASSWORD: "string",
    FormatType.BINARY: "File | Blob",
    FormatType.BYTE: "string",  # Base64
    FormatType.INT32: "number",
    FormatType.INT64: "number",
    FormatType.FLOAT: "number",
    FormatType.DOUBLE: "number",
}


# =============================================================================
# Zod Schema Mappings
# =============================================================================

ZOD_TYPES: dict[FieldType, str] = {
    FieldType.STRING: "z.string()",
    FieldType.INTEGER: "z.number().int()",
    FieldType.NUMBER: "z.number()",
    FieldType.BOOLEAN: "z.boolean()",
    FieldType.ARRAY: "z.array(z.any())",
    FieldType.OBJECT: "z.record(z.string(), z.any())",
    FieldType.NULL: "z.null()",
    FieldType.ANY: "z.any()",
}

ZOD_FORMAT_TYPES: dict[FormatType, str] = {
    FormatType.DATETIME: "z.string().datetime()",
    FormatType.DATE: "z.string().date()",
    FormatType.TIME: "z.string().time()",
    FormatType.UUID: "z.string().uuid()",
    FormatType.EMAIL: "z.string().email()",
    FormatType.URI: "z.string().url()",
    FormatType.URL: "z.string().url()",
    FormatType.HOSTNAME: "z.string()",
    FormatType.IPV4: "z.string().ip({ version: 'v4' })",
    FormatType.IPV6: "z.string().ip({ version: 'v6' })",
    FormatType.PASSWORD: "z.string()",
    FormatType.BINARY: "z.any()",  # File upload
    FormatType.BYTE: "z.string()",  # Base64
    FormatType.INT32: "z.number().int()",
    FormatType.INT64: "z.number().int()",
    FormatType.FLOAT: "z.number()",
    FormatType.DOUBLE: "z.number()",
}


# =============================================================================
# Go Type Mappings
# =============================================================================

GO_TYPES: dict[FieldType, str] = {
    FieldType.STRING: "string",
    FieldType.INTEGER: "int64",
    FieldType.NUMBER: "float64",
    FieldType.BOOLEAN: "bool",
    FieldType.ARRAY: "[]interface{}",
    FieldType.OBJECT: "map[string]interface{}",
    FieldType.NULL: "interface{}",
    FieldType.ANY: "interface{}",
}

GO_FORMAT_TYPES: dict[FormatType, str] = {
    FormatType.DATETIME: "time.Time",
    FormatType.DATE: "string",  # YYYY-MM-DD
    FormatType.TIME: "string",  # HH:MM:SS
    FormatType.UUID: "string",
    FormatType.EMAIL: "string",
    FormatType.URI: "string",
    FormatType.URL: "string",
    FormatType.HOSTNAME: "string",
    FormatType.IPV4: "string",
    FormatType.IPV6: "string",
    FormatType.PASSWORD: "string",
    FormatType.BINARY: "io.Reader",
    FormatType.BYTE: "[]byte",
    FormatType.INT32: "int32",
    FormatType.INT64: "int64",
    FormatType.FLOAT: "float32",
    FormatType.DOUBLE: "float64",
}

# Go imports needed for specific types
GO_IMPORTS: dict[str, str] = {
    "time.Time": "time",
    "io.Reader": "io",
}


# =============================================================================
# Proto Type Mappings
# =============================================================================

PROTO_TYPES: dict[FieldType, str] = {
    FieldType.STRING: "string",
    FieldType.INTEGER: "int64",
    FieldType.NUMBER: "double",
    FieldType.BOOLEAN: "bool",
    FieldType.ARRAY: "repeated",  # Needs item type
    FieldType.OBJECT: "bytes",  # JSON serialized
    FieldType.NULL: "bytes",
    FieldType.ANY: "bytes",
}

PROTO_FORMAT_TYPES: dict[FormatType, str] = {
    FormatType.DATETIME: "google.protobuf.Timestamp",
    FormatType.DATE: "string",
    FormatType.TIME: "string",
    FormatType.UUID: "string",
    FormatType.EMAIL: "string",
    FormatType.URI: "string",
    FormatType.URL: "string",
    FormatType.HOSTNAME: "string",
    FormatType.IPV4: "string",
    FormatType.IPV6: "string",
    FormatType.PASSWORD: "string",
    FormatType.BINARY: "bytes",
    FormatType.BYTE: "bytes",
    FormatType.INT32: "int32",
    FormatType.INT64: "int64",
    FormatType.FLOAT: "float",
    FormatType.DOUBLE: "double",
}

# Proto imports needed for specific types
PROTO_IMPORTS: dict[str, str] = {
    "google.protobuf.Timestamp": "google/protobuf/timestamp.proto",
    "google.protobuf.Empty": "google/protobuf/empty.proto",
}


# =============================================================================
# Type Mapper Utility
# =============================================================================


class TypeInfo(NamedTuple):
    """Type information with optional import."""

    type_str: str
    import_str: str | None = None


class TypeMapper:
    """
    Unified type mapper for all target languages.

    Provides consistent type conversion from OpenAPI types to target language types.
    Tracks required imports for generated code.
    """

    def __init__(self) -> None:
        self._python_imports: set[str] = set()
        self._go_imports: set[str] = set()
        self._proto_imports: set[str] = set()

    def reset_imports(self) -> None:
        """Reset tracked imports."""
        self._python_imports.clear()
        self._go_imports.clear()
        self._proto_imports.clear()

    # -------------------------------------------------------------------------
    # Python
    # -------------------------------------------------------------------------

    def to_python(
        self,
        field_type: FieldType | str,
        format_type: FormatType | str | None = None,
        *,
        nullable: bool = False,
    ) -> str:
        """
        Convert to Python type.

        Args:
            field_type: OpenAPI type
            format_type: Optional format specifier
            nullable: Whether type is nullable

        Returns:
            Python type string (e.g., "str", "int", "datetime")
        """
        ft = FieldType(field_type) if isinstance(field_type, str) else field_type

        # Check format first
        if format_type:
            fmt = FormatType(format_type) if isinstance(format_type, str) else format_type
            if fmt in PYTHON_FORMAT_TYPES:
                type_str = PYTHON_FORMAT_TYPES[fmt]
                if type_str in PYTHON_IMPORTS:
                    self._python_imports.add(PYTHON_IMPORTS[type_str])
                return f"{type_str} | None" if nullable else type_str

        # Base type
        type_str = PYTHON_TYPES.get(ft, "Any")
        if type_str in PYTHON_IMPORTS:
            self._python_imports.add(PYTHON_IMPORTS[type_str])

        return f"{type_str} | None" if nullable else type_str

    def get_python_imports(self) -> list[str]:
        """Get required Python imports."""
        return sorted(self._python_imports)

    # -------------------------------------------------------------------------
    # TypeScript
    # -------------------------------------------------------------------------

    def to_typescript(
        self,
        field_type: FieldType | str,
        format_type: FormatType | str | None = None,
        *,
        nullable: bool = False,
    ) -> str:
        """
        Convert to TypeScript type.

        Args:
            field_type: OpenAPI type
            format_type: Optional format specifier
            nullable: Whether type is nullable

        Returns:
            TypeScript type string
        """
        ft = FieldType(field_type) if isinstance(field_type, str) else field_type

        # Check format first
        if format_type:
            fmt = FormatType(format_type) if isinstance(format_type, str) else format_type
            if fmt in TYPESCRIPT_FORMAT_TYPES:
                type_str = TYPESCRIPT_FORMAT_TYPES[fmt]
                return f"{type_str} | null" if nullable else type_str

        # Base type
        type_str = TYPESCRIPT_TYPES.get(ft, "any")
        return f"{type_str} | null" if nullable else type_str

    # -------------------------------------------------------------------------
    # Zod
    # -------------------------------------------------------------------------

    def to_zod(
        self,
        field_type: FieldType | str,
        format_type: FormatType | str | None = None,
        *,
        nullable: bool = False,
        optional: bool = False,
    ) -> str:
        """
        Convert to Zod schema.

        Args:
            field_type: OpenAPI type
            format_type: Optional format specifier
            nullable: Whether type is nullable
            optional: Whether type is optional

        Returns:
            Zod schema string (e.g., "z.string()", "z.number().nullable()")
        """
        ft = FieldType(field_type) if isinstance(field_type, str) else field_type

        # Check format first
        if format_type:
            fmt = FormatType(format_type) if isinstance(format_type, str) else format_type
            if fmt in ZOD_FORMAT_TYPES:
                schema = ZOD_FORMAT_TYPES[fmt]
            else:
                schema = ZOD_TYPES.get(ft, "z.any()")
        else:
            schema = ZOD_TYPES.get(ft, "z.any()")

        # Add modifiers
        if nullable:
            schema = f"{schema}.nullable()"
        if optional:
            schema = f"{schema}.optional()"

        return schema

    # -------------------------------------------------------------------------
    # Go
    # -------------------------------------------------------------------------

    def to_go(
        self,
        field_type: FieldType | str,
        format_type: FormatType | str | None = None,
        *,
        optional: bool = False,
    ) -> str:
        """
        Convert to Go type.

        Args:
            field_type: OpenAPI type
            format_type: Optional format specifier
            optional: Whether to use pointer type

        Returns:
            Go type string (e.g., "string", "*int64", "time.Time")
        """
        ft = FieldType(field_type) if isinstance(field_type, str) else field_type

        # Check format first
        if format_type:
            fmt = FormatType(format_type) if isinstance(format_type, str) else format_type
            if fmt in GO_FORMAT_TYPES:
                type_str = GO_FORMAT_TYPES[fmt]
                if type_str in GO_IMPORTS:
                    self._go_imports.add(GO_IMPORTS[type_str])
                # Interfaces don't need pointers
                if type_str in {"io.Reader", "interface{}"}:
                    return type_str
                return f"*{type_str}" if optional else type_str

        # Base type
        type_str = GO_TYPES.get(ft, "interface{}")
        if type_str in GO_IMPORTS:
            self._go_imports.add(GO_IMPORTS[type_str])

        # Interfaces and maps don't need pointers
        if type_str in {"interface{}", "map[string]interface{}"}:
            return type_str

        return f"*{type_str}" if optional else type_str

    def get_go_imports(self) -> list[str]:
        """Get required Go imports."""
        return sorted(self._go_imports)

    # -------------------------------------------------------------------------
    # Proto
    # -------------------------------------------------------------------------

    def to_proto(
        self,
        field_type: FieldType | str,
        format_type: FormatType | str | None = None,
    ) -> str:
        """
        Convert to Proto type.

        Args:
            field_type: OpenAPI type
            format_type: Optional format specifier

        Returns:
            Proto type string
        """
        ft = FieldType(field_type) if isinstance(field_type, str) else field_type

        # Check format first
        if format_type:
            fmt = FormatType(format_type) if isinstance(format_type, str) else format_type
            if fmt in PROTO_FORMAT_TYPES:
                type_str = PROTO_FORMAT_TYPES[fmt]
                if type_str in PROTO_IMPORTS:
                    self._proto_imports.add(PROTO_IMPORTS[type_str])
                return type_str

        # Base type
        return PROTO_TYPES.get(ft, "bytes")

    def get_proto_imports(self) -> list[str]:
        """Get required Proto imports."""
        return sorted(self._proto_imports)
