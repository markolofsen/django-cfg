"""
Swift Type Mapper - Maps OpenAPI/IR types to Swift types.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .naming import to_pascal_case, to_camel_case, swift_property_name

if TYPE_CHECKING:
    from django_cfg.modules.django_client.core.ir import IRSchemaObject


class SwiftTypeMapper:
    """Maps IR types to Swift types."""

    # OpenAPI type → Swift type mapping
    TYPE_MAP = {
        "string": "String",
        "integer": "Int",
        "number": "Double",
        "boolean": "Bool",
        "array": "[JSONValue]",  # Will be replaced with specific type
        "object": "[String: JSONValue]",  # Will be replaced with specific type
    }

    # OpenAPI format → Swift type mapping
    FORMAT_MAP = {
        "date": "String",  # ISO date string
        "date-time": "Date",
        "time": "String",
        "email": "String",
        "uri": "String",
        "url": "String",
        "uuid": "String",
        "int32": "Int32",
        "int64": "Int64",
        "float": "Float",
        "double": "Double",
        "binary": "Data",
        "byte": "Data",
    }

    def __init__(self):
        self.known_types: set[str] = set()

    def map_type(
        self,
        schema: IRSchemaObject,
        optional: bool = False,
        in_array: bool = False,
    ) -> str:
        """
        Map IR schema to Swift type.

        Args:
            schema: IR schema object
            optional: Whether the type is optional
            in_array: Whether this is an array element type

        Returns:
            Swift type string
        """
        swift_type = self._get_base_type(schema)

        if optional and not in_array:
            swift_type = f"{swift_type}?"

        return swift_type

    def _get_base_type(self, schema: IRSchemaObject) -> str:
        """Get base Swift type for schema."""
        # Reference to another schema
        if schema.ref:
            type_name = self._ref_to_type_name(schema.ref)
            self.known_types.add(type_name)
            return type_name

        # Enum
        if schema.enum:
            if schema.name:
                return to_pascal_case(schema.name)
            return "String"

        # Array
        if schema.type == "array" and schema.items:
            item_type = self._get_base_type(schema.items)
            return f"[{item_type}]"

        # Object with additionalProperties (dictionary)
        if schema.type == "object" and schema.additional_properties:
            if isinstance(schema.additional_properties, bool):
                return "[String: JSONValue]"
            value_type = self._get_base_type(schema.additional_properties)
            return f"[String: {value_type}]"

        # Named object (will be generated as struct)
        if schema.type == "object" and schema.name:
            type_name = to_pascal_case(schema.name)
            self.known_types.add(type_name)
            return type_name

        # Format-specific mapping
        if schema.format and schema.format in self.FORMAT_MAP:
            return self.FORMAT_MAP[schema.format]

        # Basic type mapping
        if schema.type and schema.type in self.TYPE_MAP:
            return self.TYPE_MAP[schema.type]

        # Default to JSONValue for unknown types
        return "JSONValue"

    def _ref_to_type_name(self, ref: str) -> str:
        """Convert $ref to Swift type name."""
        # #/components/schemas/WorkspaceMember -> WorkspaceMember
        if ref.startswith("#/components/schemas/"):
            return ref.split("/")[-1]
        return ref.split("/")[-1]
