"""
TypeScript type conversion utilities.

Converts Pydantic models and JSON Schema to TypeScript interfaces.
Also supports IntEnum to TypeScript enum conversion.
"""

import inspect
import logging
from enum import IntEnum
from typing import Any, Dict, Type, List

from pydantic import BaseModel

from .base import get_model_schema, get_schema_properties, get_schema_required, get_schema_defs

logger = logging.getLogger(__name__)


# =============================================================================
# INTENUM TO TYPESCRIPT ENUM
# =============================================================================

def is_int_enum(type_hint: Any) -> bool:
    """Check if type hint is an IntEnum subclass."""
    try:
        return inspect.isclass(type_hint) and issubclass(type_hint, IntEnum)
    except (TypeError, AttributeError):
        return False


def int_enum_to_typescript(enum_class: Type[IntEnum]) -> str:
    """
    Convert Python IntEnum to TypeScript const enum.

    Args:
        enum_class: IntEnum subclass

    Returns:
        TypeScript const enum definition

    Example:
        >>> class ViewerType(IntEnum):
        ...     UNKNOWN = 0
        ...     CODE = 1
        >>> int_enum_to_typescript(ViewerType)
        'export const enum ViewerType {\n  UNKNOWN = 0,\n  CODE = 1,\n}'
    """
    if not is_int_enum(enum_class):
        raise ValueError(f"{enum_class} is not an IntEnum subclass")

    lines = []
    lines.append(f"export const enum {enum_class.__name__} {{")

    for member in enum_class:
        lines.append(f"  {member.name} = {member.value},")

    lines.append("}")

    return "\n".join(lines)


def generate_typescript_enums(enum_classes: List[Type[IntEnum]]) -> str:
    """
    Generate TypeScript enum definitions for multiple IntEnum classes.

    Args:
        enum_classes: List of IntEnum subclasses

    Returns:
        Complete TypeScript enum definitions
    """
    if not enum_classes:
        return ""

    lines = []
    lines.append("// Generated TypeScript Enums")
    lines.append("// Auto-generated from Python IntEnum - DO NOT EDIT")
    lines.append("")

    for enum_class in enum_classes:
        enum_code = int_enum_to_typescript(enum_class)
        lines.append(enum_code)
        lines.append("")

    return "\n".join(lines)


def _sanitize_jsdoc_description(description: str) -> str:
    """
    Sanitize description string for use in JSDoc comments.

    Handles:
    - Escape */ which would close the comment prematurely
    - Replace newlines with spaces
    - Escape single quotes in examples to avoid potential parsing issues
    """
    if not description:
        return ""
    # Replace */ to prevent closing the comment
    result = description.replace("*/", "*\\/")
    # Replace newlines with spaces
    result = result.replace("\n", " ").replace("\r", "")
    # Replace single quotes with backticks for code examples
    # This prevents issues with some TypeScript parsers
    result = result.replace("'", "`")
    return result.strip()


def convert_json_schema_to_typescript(
    field_info: Dict[str, Any],
    defs: Dict[str, Any] | None = None
) -> str:
    """
    Convert JSON schema field to TypeScript type.

    Args:
        field_info: JSON schema field information
        defs: Schema definitions ($defs) for resolving $ref

    Returns:
        str: TypeScript type string

    Examples:
        >>> convert_json_schema_to_typescript({"type": "string"})
        'string'
        >>> convert_json_schema_to_typescript({"type": "array", "items": {"type": "string"}})
        'string[]'
    """
    # Handle $ref (reference to nested model)
    if "$ref" in field_info:
        ref = field_info["$ref"]
        # Extract type name from "#/$defs/TypeName"
        if ref.startswith("#/$defs/"):
            return ref.split("/")[-1]
        return "any"

    # Handle anyOf (union types)
    if "anyOf" in field_info:
        types = [convert_json_schema_to_typescript(t, defs) for t in field_info["anyOf"]]
        return " | ".join(types)

    field_type = field_info.get("type", "any")

    type_mapping = {
        "string": "string",
        "integer": "number",
        "number": "number",
        "boolean": "boolean",
        "null": "null",
    }

    if field_type in type_mapping:
        return type_mapping[field_type]

    if field_type == "array":
        items = field_info.get("items", {})
        item_type = convert_json_schema_to_typescript(items, defs)
        return f"{item_type}[]"

    if field_type == "object":
        return "Record<string, any>"

    return "any"


def _generate_interface_from_schema(
    name: str,
    schema: Dict[str, Any],
    defs: Dict[str, Any]
) -> str:
    """
    Generate TypeScript interface from JSON schema definition.

    Args:
        name: Interface name
        schema: JSON schema for the type
        defs: Schema definitions for resolving nested $ref

    Returns:
        str: TypeScript interface definition
    """
    properties = get_schema_properties(schema)
    required = get_schema_required(schema)

    ts_fields = []
    for field_name, field_info in properties.items():
        ts_type = convert_json_schema_to_typescript(field_info, defs)
        optional = '?' if field_name not in required else ''

        description = field_info.get('description')
        if description:
            safe_desc = _sanitize_jsdoc_description(description)
            ts_fields.append(f"  /** {safe_desc} */")

        ts_fields.append(f"  {field_name}{optional}: {ts_type};")

    interface_code = f"export interface {name} {{\n"
    interface_code += "\n".join(ts_fields)
    interface_code += "\n}"

    return interface_code


def pydantic_to_typescript(model: Type[BaseModel]) -> str:
    """
    Convert Pydantic model to TypeScript interface.

    Args:
        model: Pydantic model class

    Returns:
        str: TypeScript interface definition (may include nested interfaces)
    """
    if not issubclass(model, BaseModel):
        return "any"

    try:
        schema = get_model_schema(model)
        properties = get_schema_properties(schema)
        required = get_schema_required(schema)
        defs = get_schema_defs(schema)

        # First generate nested interfaces from $defs
        # Skip enum types (they have 'enum' or 'const' in schema, or no 'properties')
        nested_interfaces = []
        for def_name, def_schema in defs.items():
            # Skip if it's an enum definition (IntEnum generates schema with 'enum' key or 'type': 'integer')
            if 'enum' in def_schema or 'const' in def_schema:
                continue
            # Skip if it has no properties (likely an enum or primitive type)
            if 'properties' not in def_schema and def_schema.get('type') == 'integer':
                continue
            nested_interface = _generate_interface_from_schema(def_name, def_schema, defs)
            nested_interfaces.append(nested_interface)

        # Generate main interface
        ts_fields = []
        for field_name, field_info in properties.items():
            ts_type = convert_json_schema_to_typescript(field_info, defs)
            optional = '?' if field_name not in required else ''

            # Add description as comment if available
            description = field_info.get('description')
            if description:
                safe_desc = _sanitize_jsdoc_description(description)
                ts_fields.append(f"  /** {safe_desc} */")

            ts_fields.append(f"  {field_name}{optional}: {ts_type};")

        interface_code = f"export interface {model.__name__} {{\n"
        interface_code += "\n".join(ts_fields)
        interface_code += "\n}"

        # Combine nested interfaces with main interface
        if nested_interfaces:
            return "\n\n".join(nested_interfaces) + "\n\n" + interface_code

        return interface_code

    except Exception as e:
        logger.error(f"Failed to convert {model.__name__} to TypeScript: {e}")
        return f"export interface {model.__name__} {{ [key: string]: any; }}"


def generate_typescript_types(models: List[Type[BaseModel]]) -> str:
    """
    Generate TypeScript type definitions for multiple Pydantic models.

    Args:
        models: List of Pydantic model classes

    Returns:
        str: Complete TypeScript type definitions
    """
    lines = []
    lines.append("// Generated TypeScript Types")
    lines.append("// Auto-generated from Pydantic models - DO NOT EDIT")
    lines.append("")

    for model in models:
        interface = pydantic_to_typescript(model)
        lines.append(interface)
        lines.append("")

    return "\n".join(lines)
