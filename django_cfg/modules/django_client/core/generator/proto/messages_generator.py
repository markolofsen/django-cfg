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
    - Enum references via $ref
    - Field numbering
    - Proper indentation and formatting
    """

    def __init__(self, type_mapper: ProtoTypeMapper):
        self.type_mapper = type_mapper
        self.generated_messages: set[str] = set()  # Track what we've generated
        self.message_definitions: list[str] = []  # Ordered list of definitions
        self.all_schemas: dict[str, IRSchemaObject] = {}  # All schemas for $ref resolution

    def _is_enum_ref(self, schema: IRSchemaObject) -> bool:
        """Check if schema is a $ref pointing to an enum schema."""
        if not schema.ref:
            return False
        ref_schema = self.all_schemas.get(schema.ref)
        return ref_schema is not None and ref_schema.enum is not None

    def _get_ref_schema(self, schema: IRSchemaObject) -> IRSchemaObject | None:
        """Get the referenced schema if it exists."""
        if not schema.ref:
            return None
        return self.all_schemas.get(schema.ref)

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

        # Generate nested enums first (inline enums only, not $ref enums)
        for prop_name, prop_schema in (schema.properties or {}).items():
            if prop_schema.enum and not prop_schema.ref:
                enum_name = self.type_mapper.get_message_name(prop_name)
                nested_enum = self._generate_enum(prop_schema, enum_name, indent=2)
                if nested_enum:
                    lines.append("")
                    lines.extend(f"  {line}" for line in nested_enum.split("\n"))

        # Generate nested messages (only if not already defined at top level)
        # Skip $ref fields that point to enums - they don't need nested messages
        for prop_name, prop_schema in (schema.properties or {}).items():
            # Skip enum refs - they're handled as separate top-level enums
            if self._is_enum_ref(prop_schema):
                continue
            # Skip $ref to existing schemas
            if prop_schema.ref:
                continue
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
                if self._is_enum_ref(field_schema.items):
                    # Array of enum refs
                    item_type = self.type_mapper.get_message_name(field_schema.items.ref)
                elif field_schema.items.ref:
                    # Array of object refs
                    item_type = self.type_mapper.get_message_name(field_schema.items.ref)
                elif field_schema.items.type == "object":
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
        elif self._is_enum_ref(field_schema):
            # Field is a $ref to an enum schema - use the enum type
            field_type = self.type_mapper.get_message_name(field_schema.ref)
        elif field_schema.ref:
            # Field is a $ref to an object schema - use the referenced type
            field_type = self.type_mapper.get_message_name(field_schema.ref)
        elif field_schema.type == "object":
            # Inline nested object
            field_type = self.type_mapper.get_message_name(field_name)
        elif field_schema.enum:
            # Inline enum field
            field_type = self.type_mapper.get_message_name(field_name)
        else:
            # Scalar field
            field_type = self.type_mapper.map_type(
                field_schema.type or "string",
                field_schema.format,
            )

        # Get field label
        label = self.type_mapper.get_field_label(is_required, is_nullable, is_repeated)

        # Add json_name option if field was renamed (for JSON compatibility)
        json_name_option = ""
        if proto_field_name != field_name:
            json_name_option = f' [json_name = "{field_name}"]'

        # Build field definition
        if label:
            return f"{label} {field_type} {proto_field_name} = {field_number}{json_name_option};"
        else:
            return f"{field_type} {proto_field_name} = {field_number}{json_name_option};"

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

        Note:
            Uses json_compatible=True by default for REST API compatibility.
            Enum values preserve original casing (e.g., "email", "phone")
            so SwiftProtobuf JSON encoding matches Django expectations.
            The default "unknown" value is prefixed with the enum name to avoid
            conflicts when multiple enums are defined in the same message scope.
        """
        if not schema.enum:
            return ""

        indent_str = " " * indent
        lines = [f"{indent_str}enum {enum_name} {{"]

        # Proto enums must start with 0
        # Add "unknown" as first value if not present
        enum_values = list(schema.enum)
        has_unknown = any(
            str(v).lower() in ("unknown", "unspecified")
            for v in enum_values
        )

        # Import sanitize_enum_value at the top of the method
        from .naming import sanitize_enum_value

        if not has_unknown:
            # Prefix "unknown" with enum name to avoid C++ scoping conflicts
            # Proto enums in C++ are siblings of their parent message, not children
            unknown_value_name = sanitize_enum_value("unknown", enum_name, json_compatible=False)
            lines.append(f"{indent_str}  {unknown_value_name} = 0;")
            start_index = 1
        else:
            start_index = 0

        # Generate enum values
        for idx, value in enumerate(enum_values, start=start_index):
            # Use prefixed names for "unknown"/"unspecified" to avoid conflicts
            # Use json_compatible=True for other values to preserve original casing
            value_str = str(value).lower()
            if value_str in ("unknown", "unspecified"):
                enum_value_name = sanitize_enum_value(value, enum_name, json_compatible=False)
            else:
                enum_value_name = sanitize_enum_value(value, enum_name, json_compatible=True)
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
        self.all_schemas = schemas  # Store for $ref resolution

        # First pass: generate enums from top-level enum schemas
        for schema_name, schema in schemas.items():
            if schema.enum:
                enum_name = self.type_mapper.get_message_name(schema_name)
                if enum_name not in self.generated_messages:
                    self.generated_messages.add(enum_name)
                    enum_def = self._generate_enum(schema, enum_name)
                    if enum_def:
                        self.message_definitions.append(enum_def)

        # Second pass: generate messages
        for schema_name, schema in schemas.items():
            if not schema.enum:  # Skip enums (already generated)
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
