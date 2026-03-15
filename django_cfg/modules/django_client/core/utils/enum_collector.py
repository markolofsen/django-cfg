"""
EnumCollector - Extracts and processes enum schemas from IR.

Extracted from BaseGenerator._collect_enums_from_schemas for independent testability.
"""
from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..ir import IRSchemaObject

_RE_NON_ALNUM = re.compile(r'[^a-zA-Z0-9]')
_RE_MULTI_UNDERSCORE = re.compile(r'_+')


class EnumCollector:
    """
    Collects and processes enum schemas from a schema dict.

    Handles:
    - Recursive traversal of nested schemas
    - Auto-generation of enum_var_names when missing
    - Deduplication by schema name
    """

    def __init__(self, all_schemas: dict[str, "IRSchemaObject"]):
        self._all_schemas = all_schemas
        self._enums: dict[str, "IRSchemaObject"] = {}

    def collect(self, schemas: dict[str, "IRSchemaObject"]) -> dict[str, "IRSchemaObject"]:
        """Collect all enum schemas reachable from the given schemas."""
        self._enums = {}
        for schema in schemas.values():
            self._visit(schema)
        return self._enums

    def _auto_var_names(self, schema: "IRSchemaObject") -> "IRSchemaObject":
        """Auto-generate enum_var_names from enum values if missing."""
        if schema.enum and not schema.enum_var_names:
            # Generate variable names from values
            var_names = []
            for value in schema.enum:
                if isinstance(value, str):
                    # Convert "waiting_for_user" → "WAITING_FOR_USER"
                    # Replace all non-alphanumeric chars with underscore
                    var_name = _RE_NON_ALNUM.sub('_', value.upper())
                    # Collapse multiple underscores
                    var_name = _RE_MULTI_UNDERSCORE.sub('_', var_name).strip('_')
                else:
                    # For integers: 1 → "VALUE_1"
                    var_name = f"VALUE_{value}"
                # Identifiers cannot start with a digit in most languages
                if var_name and var_name[0].isdigit():
                    var_name = '_' + var_name
                var_names.append(var_name)

            # Create new schema with auto-generated var names
            from ..ir import IRSchemaObject
            schema = IRSchemaObject(
                **{**schema.model_dump(), "enum_var_names": var_names}
            )
        return schema

    def _visit(self, schema: "IRSchemaObject") -> None:
        """Recursively visit schema and collect enums."""
        # Check if this schema itself is an enum (with or without x-enum-varnames)
        if schema.enum and schema.name:
            schema = self._auto_var_names(schema)
            self._enums[schema.name] = schema

        # Check if this schema is a reference to an enum
        if schema.ref and schema.ref in self._all_schemas:
            ref_schema = self._all_schemas[schema.ref]
            if ref_schema.enum:
                ref_schema = self._auto_var_names(ref_schema)
                self._enums[ref_schema.name] = ref_schema

        # Check properties for enums
        if schema.properties:
            for prop_schema in schema.properties.values():
                # If property has enum, it's a standalone enum
                if prop_schema.enum and prop_schema.name:
                    prop_schema = self._auto_var_names(prop_schema)
                    self._enums[prop_schema.name] = prop_schema
                # Check if property is a reference to an enum
                elif prop_schema.ref and prop_schema.ref in self._all_schemas:
                    ref_schema = self._all_schemas[prop_schema.ref]
                    if ref_schema.enum:
                        ref_schema = self._auto_var_names(ref_schema)
                        self._enums[ref_schema.name] = ref_schema
                # Recurse into nested objects
                elif prop_schema.type == "object":
                    self._visit(prop_schema)
                # Recurse into arrays
                elif prop_schema.type == "array" and prop_schema.items:
                    if prop_schema.items.enum and prop_schema.items.name:
                        items = self._auto_var_names(prop_schema.items)
                        self._enums[items.name] = items
                    elif prop_schema.items.ref and prop_schema.items.ref in self._all_schemas:
                        ref_items = self._all_schemas[prop_schema.items.ref]
                        if ref_items.enum:
                            ref_items = self._auto_var_names(ref_items)
                            self._enums[ref_items.name] = ref_items
                    elif prop_schema.items.type == "object":
                        self._visit(prop_schema.items)

        # Check array items for enums (if schema itself is array)
        if schema.items:
            if schema.items.enum and schema.items.name:
                items = self._auto_var_names(schema.items)
                self._enums[items.name] = items
            elif schema.items.ref and schema.items.ref in self._all_schemas:
                ref_items = self._all_schemas[schema.items.ref]
                if ref_items.enum:
                    ref_items = self._auto_var_names(ref_items)
                    self._enums[ref_items.name] = ref_items
            elif schema.items.type == "object":
                self._visit(schema.items)
