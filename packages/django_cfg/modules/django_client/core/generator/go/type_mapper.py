"""
Type mapping from OpenAPI/IR to Go types.

Handles conversion of IR schemas to Go types with proper handling of:
- Primitive types (string, integer, number, boolean)
- Optional fields (pointers)
- Arrays and slices
- Nested objects (struct references)
- Enums (custom types)
- Format-specific types (time.Time, uuid, etc.)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .naming import sanitize_go_identifier, to_pascal_case

if TYPE_CHECKING:
    from ...ir import IRSchemaObject


class GoTypeMapper:
    """
    Maps OpenAPI/IR types to Go types.

    Handles:
    - Primitive types (string → string, integer → int64, etc.)
    - Optional fields (User.email? → *string)
    - Arrays ([]string, []int64)
    - Nested objects (references to other structs)
    - Enums (custom types with constants)
    """

    # Primitive type mapping
    PRIMITIVE_TYPES = {
        "string": "string",
        "integer": "int64",
        "number": "float64",
        "boolean": "bool",
        "object": "map[string]interface{}",
        "null": "interface{}",
    }

    # Format-specific type overrides
    FORMAT_OVERRIDES = {
        "int32": "int32",
        "int64": "int64",
        "float": "float32",
        "double": "float64",
        "date-time": "time.Time",
        "date": "string",  # YYYY-MM-DD format
        "uuid": "string",  # Or use google/uuid package
        "binary": "io.Reader",  # For file uploads in multipart forms
        "byte": "[]byte",
        "email": "string",
        "uri": "string",
        "url": "string",
        "hostname": "string",
        "ipv4": "string",
        "ipv6": "string",
    }

    def __init__(self, use_types_package: bool = False):
        """Initialize type mapper.

        Args:
            use_types_package: If True, prefix enum types with "types."
        """
        self._imports_needed = set()
        self.use_types_package = use_types_package

    def get_imports(self) -> set[str]:
        """
        Get required imports for generated code.

        Returns:
            Set of import paths (e.g., {"time", "encoding/json"})
        """
        return self._imports_needed

    def ir_schema_to_go_type(
        self,
        schema: IRSchemaObject,
        required: bool = True,
        parent_schema: IRSchemaObject | None = None,
    ) -> str:
        """
        Convert IR schema to Go type.

        Args:
            schema: IRSchemaObject to convert
            required: Whether field is required (affects pointer usage)
            parent_schema: Parent schema (for context)

        Returns:
            Go type string

        Examples:
            >>> mapper.ir_schema_to_go_type(
            ...     IRSchemaObject(name="email", type="string"),
            ...     required=False
            ... )
            '*string'

            >>> mapper.ir_schema_to_go_type(
            ...     IRSchemaObject(name="items", type="array", items=IRSchemaObject(type="string"))
            ... )
            '[]string'

            >>> mapper.ir_schema_to_go_type(
            ...     IRSchemaObject(name="created_at", type="string", format="date-time")
            ... )
            'time.Time'
        """
        # Handle $ref
        if schema.ref:
            type_name = schema.ref.split('/')[-1]
            # Struct references are already pointers in Go when optional
            if not required:
                return f"*{type_name}"
            return type_name

        # Handle enums
        if schema.enum:
            enum_type = self._get_enum_type_name(schema)
            if self.use_types_package:
                enum_type = f"types.{enum_type}"
            return f"*{enum_type}" if not required else enum_type

        # Handle arrays
        if schema.type == "array" and schema.items:
            item_type = self.ir_schema_to_go_type(schema.items, required=True)
            # Arrays are always non-nil in Go, but can be empty
            # omitempty in JSON tag handles the serialization
            return f"[]{item_type}"

        # Handle format overrides
        if schema.format and schema.format in self.FORMAT_OVERRIDES:
            go_type = self.FORMAT_OVERRIDES[schema.format]

            # Track imports
            if go_type == "time.Time":
                self._imports_needed.add("time")
            elif go_type == "io.Reader":
                self._imports_needed.add("io")

            # io.Reader is an interface - don't use pointer for interfaces
            # time.Time is a struct, so we use pointer for optionals
            if not required:
                # Interfaces in Go are already reference types, no pointer needed
                if go_type == "io.Reader":
                    return go_type
                return f"*{go_type}"
            return go_type

        # Handle primitive types
        if schema.type in self.PRIMITIVE_TYPES:
            go_type = self.PRIMITIVE_TYPES[schema.type]

            # Optionals become pointers (except for maps and interfaces)
            if not required and go_type not in ["interface{}", "map[string]interface{}"]:
                return f"*{go_type}"

            return go_type

        # Fallback to interface{} for unknown types
        return "interface{}"

    def ir_schema_to_struct(
        self,
        schema: IRSchemaObject,
    ) -> dict:
        """
        Convert IR schema to Go struct definition.

        Args:
            schema: IRSchemaObject to convert

        Returns:
            Dictionary with struct definition:
            {
                "name": "User",
                "fields": [
                    {
                        "name": "ID",
                        "type": "int64",
                        "json_tag": '`json:"id"`',
                        "description": "User ID",
                        "required": True
                    },
                    ...
                ],
                "doc": "User represents a registered user.",
                "needs_time_import": False,
            }

        Examples:
            >>> schema = IRSchemaObject(
            ...     name="User",
            ...     type="object",
            ...     properties={
            ...         "id": IRSchemaObject(name="id", type="integer"),
            ...         "username": IRSchemaObject(name="username", type="string"),
            ...         "email": IRSchemaObject(name="email", type="string"),
            ...     },
            ...     required=["id", "username"],
            ... )
            >>> struct = mapper.ir_schema_to_struct(schema)
            >>> struct["name"]
            'User'
            >>> len(struct["fields"])
            3
        """
        fields = []

        # Reset imports for this struct
        self._imports_needed = set()

        # Process properties
        for prop_name, prop_schema in (schema.properties or {}).items():
            is_required = prop_name in (schema.required or [])

            # Get Go type
            go_type = self.ir_schema_to_go_type(prop_schema, is_required, parent_schema=schema)

            # Build JSON tag
            if not is_required:
                json_tag = f'`json:"{prop_name},omitempty"`'
            else:
                json_tag = f'`json:"{prop_name}"`'

            # Create field definition
            field = {
                "name": to_pascal_case(prop_name),
                "type": go_type,
                "json_tag": json_tag,
                "description": prop_schema.description or "",
                "required": is_required,
                "deprecated": prop_schema.deprecated,
            }
            fields.append(field)

        return {
            "name": schema.name,
            "fields": fields,
            "doc": schema.description or f"{schema.name} model.",
            "needs_time_import": "time" in self._imports_needed,
        }

    def _get_enum_type_name(self, schema: IRSchemaObject) -> str:
        """
        Get enum type name from schema.

        Args:
            schema: IRSchemaObject with enum

        Returns:
            Enum type name (PascalCase)

        Examples:
            >>> schema = IRSchemaObject(name="status", type="integer", enum=[1, 2, 3])
            >>> mapper._get_enum_type_name(schema)
            'Status'

            >>> schema = IRSchemaObject(name="User.role", type="string", enum=["admin", "user"])
            >>> mapper._get_enum_type_name(schema)
            'UserRole'
        """
        if not schema.name:
            return "Enum"

        # Handle nested enum names (e.g., "User.role" → "UserRole")
        if '.' in schema.name:
            parts = schema.name.split('.')
            return ''.join(to_pascal_case(p) for p in parts)

        return to_pascal_case(schema.name)

    def get_enum_base_type(self, schema: IRSchemaObject) -> str:
        """
        Get Go base type for enum.

        Args:
            schema: IRSchemaObject with enum

        Returns:
            Go base type ("int64", "string", etc.)

        Examples:
            >>> schema = IRSchemaObject(name="status", type="integer", enum=[1, 2, 3])
            >>> mapper.get_enum_base_type(schema)
            'int64'

            >>> schema = IRSchemaObject(name="role", type="string", enum=["admin", "user"])
            >>> mapper.get_enum_base_type(schema)
            'string'
        """
        if schema.type == "integer":
            # Check format for int32 vs int64
            if schema.format == "int32":
                return "int32"
            return "int64"
        elif schema.type == "number":
            if schema.format == "float":
                return "float32"
            return "float64"
        elif schema.type == "string":
            return "string"

        # Default to int64
        return "int64"

    def generate_enum_definition(self, schema: IRSchemaObject) -> dict:
        """
        Generate enum type definition for Go.

        Args:
            schema: IRSchemaObject with enum + enum_var_names

        Returns:
            Dictionary with enum definition:
            {
                "name": "StatusEnum",
                "base_type": "int64",
                "values": [
                    {"name": "StatusNew", "value": 1, "description": "New user"},
                    {"name": "StatusActive", "value": 2, "description": "Active user"},
                ],
                "doc": "StatusEnum represents user status.",
            }

        Examples:
            >>> schema = IRSchemaObject(
            ...     name="status",
            ...     type="integer",
            ...     enum=[1, 2, 3],
            ...     enum_var_names=["STATUS_NEW", "STATUS_ACTIVE", "STATUS_COMPLETE"],
            ... )
            >>> enum_def = mapper.generate_enum_definition(schema)
            >>> enum_def["name"]
            'Status'
            >>> len(enum_def["values"])
            3
        """
        enum_type_name = self._get_enum_type_name(schema)
        base_type = self.get_enum_base_type(schema)

        # Build enum values
        values = []
        enum_values = schema.enum or []
        enum_var_names = schema.enum_var_names or []

        for i, enum_value in enumerate(enum_values):
            # Get variable name
            if i < len(enum_var_names):
                # Even if var name is provided, sanitize it for Go
                var_name = sanitize_go_identifier(enum_var_names[i])
            else:
                # Auto-generate from value
                if isinstance(enum_value, str):
                    # Use sanitize_go_identifier to handle dots, hyphens, spaces, etc.
                    var_name = sanitize_go_identifier(enum_value)
                else:
                    var_name = f"VALUE_{enum_value}"

            # var_name is now always PascalCase from sanitize_go_identifier
            go_var_name = var_name

            # Add enum type prefix if not present
            if not go_var_name.startswith(enum_type_name):
                go_var_name = enum_type_name + go_var_name

            values.append({
                "name": go_var_name,
                "value": enum_value,
                "description": "",  # Could extract from x-choices if available
            })

        return {
            "name": enum_type_name,
            "base_type": base_type,
            "values": values,
            "doc": schema.description or f"{enum_type_name} enum.",
            "is_string_enum": schema.type == "string",
        }
