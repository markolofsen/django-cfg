"""
Swift Models Generator - Generates Codable structs from IR schemas.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .type_mapper import SwiftTypeMapper
from .naming import to_pascal_case, to_camel_case, swift_property_name, SWIFT_TYPE_CONFLICTS, SWIFT_KEYWORDS

if TYPE_CHECKING:
    from django_cfg.modules.django_client.core.ir import IRSchemaObject


class SwiftModelsGenerator:
    """Generates Swift Codable structs from IR schemas."""

    def __init__(
        self,
        type_mapper: SwiftTypeMapper,
    ):
        self.type_mapper = type_mapper
        # Track generated types within this group to avoid re-generating
        self.generated_types: set[str] = set()

    def generate_models(
        self,
        schemas: dict[str, IRSchemaObject],
        group_name: str,
    ) -> str:
        """
        Generate Swift models for all schemas.

        Args:
            schemas: Dictionary of schema name -> IRSchemaObject
            group_name: API group name for file header

        Returns:
            Swift source code string
        """
        lines = [
            f"// {group_name.title()}Types.swift",
            "// Auto-generated from OpenAPI schema - DO NOT EDIT",
            "",
            "import Foundation",
            "",
        ]

        # Generate enums first
        enums = []
        structs = []
        typealiases = []

        for name, schema in sorted(schemas.items()):
            if self._should_skip_schema(name, schema):
                continue

            # Generate typealias for Paginated* types
            if name.startswith("Paginated"):
                typealias_code = self._generate_paginated_typealias(name, schema)
                if typealias_code:
                    typealiases.append(typealias_code)
                continue

            if schema.enum:
                enum_code = self._generate_enum(name, schema)
                if enum_code:
                    enums.append(enum_code)
            elif schema.type == "object" or schema.properties:
                struct_code = self._generate_struct(name, schema)
                if struct_code:
                    structs.append(struct_code)

        # Add enums
        if enums:
            lines.append("// MARK: - Enums")
            lines.append("")
            lines.extend(enums)

        # Add structs
        if structs:
            lines.append("// MARK: - Models")
            lines.append("")
            lines.extend(structs)

        # Add typealiases for paginated responses
        if typealiases:
            lines.append("// MARK: - Paginated Response Types")
            lines.append("")
            lines.extend(typealiases)

        return "\n".join(lines)

    def _should_skip_schema(self, name: str, schema: IRSchemaObject) -> bool:
        """Check if schema should be skipped."""
        # Skip request schemas - usually same as model
        if name.endswith("Request") and not schema.properties:
            return True
        return False

    def _generate_paginated_typealias(self, name: str, schema: IRSchemaObject) -> str:
        """Generate typealias for Paginated* types using generic PaginatedResponse<T>."""
        type_name = to_pascal_case(name)
        if type_name in self.generated_types:
            return ""
        self.generated_types.add(type_name)

        # Extract item type from 'results' property
        properties = schema.properties or {}
        results_schema = properties.get("results")

        if not results_schema:
            return ""

        # Get the item type from the array
        item_type = "JSONValue"  # fallback
        if results_schema.items:
            item_type = self.type_mapper.map_type(results_schema.items, optional=False)

        return f"public typealias {type_name} = PaginatedResponse<{item_type}>\n"

    def _generate_enum(self, name: str, schema: IRSchemaObject) -> str:
        """Generate Swift enum from schema."""
        if not schema.enum:
            return ""

        type_name = to_pascal_case(name)
        if type_name in self.generated_types:
            return ""
        self.generated_types.add(type_name)

        lines = [
            f"public enum {type_name}: String, Codable, CaseIterable, Sendable {{",
        ]

        for value in schema.enum:
            str_value = str(value)
            # Skip empty enum values
            if not str_value or not str_value.strip():
                continue
            case_name = to_camel_case(str_value)
            # Skip if case_name is empty after conversion
            if not case_name:
                continue
            # Swift identifiers can't start with a digit
            if case_name[0].isdigit():
                case_name = f"n{case_name}"
            if case_name != str_value:
                lines.append(f'    case {case_name} = "{value}"')
            else:
                lines.append(f"    case {case_name}")

        lines.append("}")
        lines.append("")

        return "\n".join(lines)

    def _generate_struct(self, name: str, schema: IRSchemaObject) -> str:
        """Generate Swift struct from schema."""
        type_name = to_pascal_case(name)
        if type_name in self.generated_types:
            return ""
        self.generated_types.add(type_name)

        # Collect properties
        properties = schema.properties or {}
        required = set(schema.required or [])

        if not properties:
            return ""

        # Collect inline enums first
        inline_enums: list[tuple[str, str, list]] = []  # [(enum_name, prop_name, values), ...]
        for prop_name, prop_schema in properties.items():
            if prop_schema.enum and not prop_schema.ref:
                enum_name = to_pascal_case(prop_name)
                # Handle Swift metatype conflicts (foo.Type is reserved syntax)
                if enum_name in SWIFT_TYPE_CONFLICTS:
                    enum_name = f"{enum_name}Value"
                inline_enums.append((enum_name, prop_name, prop_schema.enum))

        # Determine protocols
        protocols = ["Codable", "Sendable"]
        if "id" in properties:
            protocols.insert(0, "Identifiable")

        protocols_str = ", ".join(protocols)

        lines = [
            f"public struct {type_name}: {protocols_str} {{",
        ]

        # Generate nested enums first
        for enum_name, prop_name, enum_values in inline_enums:
            lines.append(f"    public enum {enum_name}: String, Codable, Sendable {{")
            for value in enum_values:
                str_value = str(value)
                # Skip empty enum values
                if not str_value or not str_value.strip():
                    continue
                case_name = to_camel_case(str_value)
                # Skip if case_name is empty after conversion
                if not case_name:
                    continue
                # Swift identifiers can't start with a digit
                if case_name[0].isdigit():
                    case_name = f"n{case_name}"
                if case_name != str_value:
                    lines.append(f'        case {case_name} = "{value}"')
                else:
                    lines.append(f"        case {case_name}")
            lines.append("    }")
            lines.append("")

        # Build map of prop_name -> enum_name for property generation
        enum_map = {prop_name: enum_name for enum_name, prop_name, _ in inline_enums}

        # Generate properties
        coding_keys_needed = False
        coding_keys = []

        for prop_name, prop_schema in sorted(properties.items()):
            swift_name = swift_property_name(prop_name)
            is_required = prop_name in required
            # Field is optional if: not required OR nullable
            # A field can be required (must be present in JSON) but still nullable (can have null value)
            is_optional = not is_required or prop_schema.nullable

            # Use nested enum type for inline enums
            if prop_name in enum_map:
                swift_type = enum_map[prop_name]
                if is_optional:
                    swift_type = f"{swift_type}?"
            else:
                swift_type = self.type_mapper.map_type(prop_schema, optional=is_optional)

            lines.append(f"    public let {swift_name}: {swift_type}")

            # Track if CodingKeys are needed
            if swift_name != prop_name or swift_name.startswith("`"):
                coding_keys_needed = True
            coding_keys.append((swift_name, prop_name))

        # Add CodingKeys if needed
        if coding_keys_needed:
            lines.append("")
            lines.append("    enum CodingKeys: String, CodingKey {")
            for swift_name, json_name in coding_keys:
                clean_name = swift_name.strip("`")
                # Use backticks for Swift keywords in CodingKeys
                case_identifier = f"`{clean_name}`" if clean_name in SWIFT_KEYWORDS else clean_name
                if clean_name != json_name:
                    lines.append(f'        case {case_identifier} = "{json_name}"')
                else:
                    lines.append(f"        case {case_identifier}")
            lines.append("    }")

        lines.append("}")
        lines.append("")

        return "\n".join(lines)
