"""
Proto Messages Generator - Generates Protocol Buffer message definitions from IR schemas.

Converts IRSchemaObject instances into proto3 message definitions.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .type_mapper import ProtoTypeMapper

if TYPE_CHECKING:
    from django_cfg.modules.django_client.core.ir.schema import IRSchemaObject


class ProtoMessagesGenerator:
    """
    Generates Protocol Buffer message definitions from IR schemas.

    Handles:
    - Basic message structure with fields
    - Nested message definitions
    - Enums (from string enums in OpenAPI)
    - Field numbering
    - Proper indentation and formatting
    """

    def __init__(self, type_mapper: ProtoTypeMapper):
        self.type_mapper = type_mapper
        self.generated_messages: set[str] = set()  # Track what we've generated
        self.message_definitions: list[str] = []  # Ordered list of definitions

    def generate_message(
        self, schema: IRSchemaObject, message_name: str | None = None
    ) -> str:
        """
        Generate a proto message from an IR schema.

        Args:
            schema: IR schema object to convert
            message_name: Override message name (uses schema.name if not provided)

        Returns:
            Proto message definition string
        """
        if message_name is None:
            message_name = self.type_mapper.get_message_name(schema.name or "Message")

        # Skip if already generated
        if message_name in self.generated_messages:
            return ""

        self.generated_messages.add(message_name)

        # Handle different schema types
        if schema.type == "object":
            return self._generate_object_message(schema, message_name)
        elif schema.type == "array":
            # Arrays are handled as repeated fields, not separate messages
            return ""
        elif schema.enum:
            return self._generate_enum(schema, message_name)
        else:
            # Scalar types don't need messages
            return ""

    def _generate_object_message(self, schema: IRSchemaObject, message_name: str) -> str:
        """Generate a message for an object schema."""
        lines = [f"message {message_name} {{"]

        # Generate nested enums first
        for prop_name, prop_schema in (schema.properties or {}).items():
            if prop_schema.enum:
                enum_name = self.type_mapper.get_message_name(prop_name)
                nested_enum = self._generate_enum(prop_schema, enum_name, indent=2)
                if nested_enum:
                    lines.append("")
                    lines.extend(f"  {line}" for line in nested_enum.split("\n"))

        # Generate nested messages (only if not already defined at top level)
        for prop_name, prop_schema in (schema.properties or {}).items():
            if prop_schema.type == "object" and not prop_schema.enum:
                nested_name = self.type_mapper.get_message_name(prop_name)
                # Skip if this message is already generated (it's a top-level schema)
                if nested_name not in self.generated_messages:
                    self.generated_messages.add(nested_name)
                    nested_msg = self._generate_object_message(prop_schema, nested_name)
                    if nested_msg:
                        lines.append("")
                        lines.extend(f"  {line}" for line in nested_msg.split("\n"))

        # Generate fields
        field_number = 1
        if schema.properties:
            lines.append("")
            for prop_name, prop_schema in schema.properties.items():
                field_def = self._generate_field(
                    prop_name, prop_schema, field_number, schema.required or []
                )
                lines.append(f"  {field_def}")
                field_number += 1

        lines.append("}")

        definition = "\n".join(lines)
        self.message_definitions.append(definition)
        return definition

    def _generate_field(
        self,
        field_name: str,
        field_schema: IRSchemaObject,
        field_number: int,
        required_fields: list[str],
    ) -> str:
        """
        Generate a single field definition.

        Args:
            field_name: Original field name
            field_schema: Field schema
            field_number: Proto field number
            required_fields: List of required field names

        Returns:
            Field definition line (e.g., "optional string name = 1;")
        """
        # Sanitize field name
        proto_field_name = self.type_mapper.sanitize_field_name(field_name)

        # Determine if field is required/nullable
        is_required = field_name in required_fields
        is_nullable = field_schema.nullable or False
        is_repeated = field_schema.type == "array"

        # Get field type
        if is_repeated:
            # Array field - use items type
            if field_schema.items:
                if field_schema.items.type == "object":
                    # Nested object array
                    item_type = self.type_mapper.get_message_name(field_name + "Item")
                    # Generate the nested message
                    self.generate_message(field_schema.items, item_type)
                elif field_schema.items.enum:
                    # Enum array - generate the enum definition
                    item_type = self.type_mapper.get_message_name(field_name)
                    # Generate the enum if not already generated
                    if item_type not in self.generated_messages:
                        self.generated_messages.add(item_type)
                        enum_def = self._generate_enum(field_schema.items, item_type)
                        if enum_def:
                            self.message_definitions.append(enum_def)
                else:
                    # Scalar array
                    item_type = self.type_mapper.map_type(
                        field_schema.items.type or "string",
                        field_schema.items.format,
                    )
            else:
                item_type = "string"  # Fallback
            field_type = item_type
        elif field_schema.type == "object":
            # Nested object
            field_type = self.type_mapper.get_message_name(field_name)
        elif field_schema.enum:
            # Enum field
            field_type = self.type_mapper.get_message_name(field_name)
        else:
            # Scalar field
            field_type = self.type_mapper.map_type(
                field_schema.type or "string",
                field_schema.format,
            )

        # Get field label
        label = self.type_mapper.get_field_label(is_required, is_nullable, is_repeated)

        # Build field definition
        if label:
            return f"{label} {field_type} {proto_field_name} = {field_number};"
        else:
            return f"{field_type} {proto_field_name} = {field_number};"

    def _generate_enum(
        self, schema: IRSchemaObject, enum_name: str, indent: int = 0
    ) -> str:
        """
        Generate an enum definition.

        Args:
            schema: Schema with enum values
            enum_name: Enum name
            indent: Indentation level for nested enums

        Returns:
            Enum definition string
        """
        if not schema.enum:
            return ""

        indent_str = " " * indent
        lines = [f"{indent_str}enum {enum_name} {{"]

        # Proto enums must start with 0
        # Add UNKNOWN/UNSPECIFIED as first value if not present
        enum_values = list(schema.enum)
        if not any(
            v.upper() in ("UNKNOWN", "UNSPECIFIED", f"{enum_name}_UNKNOWN")
            for v in enum_values
        ):
            lines.append(f"{indent_str}  {enum_name.upper()}_UNKNOWN = 0;")
            start_index = 1
        else:
            start_index = 0

        # Generate enum values
        for idx, value in enumerate(enum_values, start=start_index):
            # Convert to UPPER_SNAKE_CASE
            enum_value_name = (
                str(value).replace("-", "_").replace(" ", "_").replace(".", "_").upper()
            )
            # Add enum name prefix if not already present
            if not enum_value_name.startswith(enum_name.upper()):
                enum_value_name = f"{enum_name.upper()}_{enum_value_name}"

            lines.append(f"{indent_str}  {enum_value_name} = {idx};")

        lines.append(f"{indent_str}}}")

        return "\n".join(lines)

    def generate_all_messages(self, schemas: dict[str, IRSchemaObject]) -> list[str]:
        """
        Generate all message definitions from a collection of schemas.

        Args:
            schemas: Dictionary of schema_name -> IRSchemaObject

        Returns:
            List of proto message definition strings
        """
        self.generated_messages.clear()
        self.message_definitions.clear()

        for schema_name, schema in schemas.items():
            message_name = self.type_mapper.get_message_name(schema_name)
            self.generate_message(schema, message_name)

        return self.message_definitions

    def get_all_definitions(self) -> str:
        """
        Get all generated message definitions as a single string.

        Returns:
            Combined proto definitions separated by blank lines
        """
        return "\n\n".join(self.message_definitions)
