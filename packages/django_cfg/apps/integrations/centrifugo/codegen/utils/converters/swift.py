"""
Swift type conversion utilities.

Converts Pydantic models and JSON Schema to Swift Codable structs.
Also supports IntEnum to Swift enum conversion.
"""

import inspect
import logging
from enum import IntEnum
from typing import Any, Dict, Type, List

from pydantic import BaseModel

from .base import (
    get_model_schema,
    get_schema_properties,
    get_schema_required,
    get_schema_defs,
    is_optional_anyof,
    extract_ref_name,
)
from ..naming import to_camel_case, get_safe_swift_type_name

logger = logging.getLogger(__name__)


# =============================================================================
# INTENUM TO SWIFT ENUM
# =============================================================================

def is_int_enum(type_hint: Any) -> bool:
    """Check if type hint is an IntEnum subclass."""
    try:
        return inspect.isclass(type_hint) and issubclass(type_hint, IntEnum)
    except (TypeError, AttributeError):
        return False


def int_enum_to_swift(enum_class: Type[IntEnum]) -> str:
    """
    Convert Python IntEnum to Swift enum with Int raw value.

    Args:
        enum_class: IntEnum subclass

    Returns:
        Swift enum definition

    Example:
        >>> class ViewerType(IntEnum):
        ...     UNKNOWN = 0
        ...     CODE = 1
        >>> int_enum_to_swift(ViewerType)
        'public enum ViewerType: Int, Codable, Sendable {\n    case unknown = 0\n    case code = 1\n}'
    """
    if not is_int_enum(enum_class):
        raise ValueError(f"{enum_class} is not an IntEnum subclass")

    lines = []
    lines.append(f"public enum {enum_class.__name__}: Int, Codable, Sendable {{")

    for member in enum_class:
        # Convert UPPER_CASE to camelCase for Swift convention
        case_name = to_camel_case(member.name.lower())
        lines.append(f"    case {case_name} = {member.value}")

    lines.append("}")

    return "\n".join(lines)


def generate_swift_enums(enum_classes: List[Type[IntEnum]]) -> str:
    """
    Generate Swift enum definitions for multiple IntEnum classes.

    Args:
        enum_classes: List of IntEnum subclasses

    Returns:
        Complete Swift enum definitions
    """
    if not enum_classes:
        return ""

    lines = []
    lines.append("// MARK: - Enums")
    lines.append("")

    for enum_class in enum_classes:
        enum_code = int_enum_to_swift(enum_class)
        lines.append(enum_code)
        lines.append("")

    return "\n".join(lines)


def convert_json_schema_to_swift(
    field_info: Dict[str, Any],
    defs: Dict[str, Any] | None = None
) -> str:
    """
    Convert JSON schema field to Swift type.

    Args:
        field_info: JSON schema field information
        defs: Schema definitions ($defs) for resolving $ref

    Returns:
        str: Swift type string

    Examples:
        >>> convert_json_schema_to_swift({"type": "string"})
        'String'
        >>> convert_json_schema_to_swift({"type": "integer"})
        'Int64'
        >>> convert_json_schema_to_swift({"type": "array", "items": {"type": "string"}})
        '[String]'
    """
    # Handle $ref (reference to nested model)
    if "$ref" in field_info:
        ref_name = extract_ref_name(field_info["$ref"])
        # Apply Swift-safe naming to avoid conflicts with SwiftUI types
        return get_safe_swift_type_name(ref_name)

    # Handle anyOf (union types) - Swift doesn't have union types
    if "anyOf" in field_info:
        is_optional, non_null_type = is_optional_anyof(field_info)
        if is_optional and non_null_type:
            swift_type = convert_json_schema_to_swift(non_null_type, defs)
            if not swift_type.endswith("?"):
                return f"{swift_type}?"
            return swift_type
        else:
            # True union type - use AnyCodable
            return "AnyCodable"

    field_type = field_info.get("type", "AnyCodable")

    # Map JSON schema types to Swift types
    type_mapping = {
        "string": "String",
        "integer": "Int",
        "number": "Double",
        "boolean": "Bool",
        "null": "AnyCodable",
    }

    if field_type in type_mapping:
        return type_mapping[field_type]

    if field_type == "array":
        items = field_info.get("items", {})
        # Empty items dict means untyped array
        if not items:
            return "[AnyCodable]"
        item_type = convert_json_schema_to_swift(items, defs)
        return f"[{item_type}]"

    if field_type == "object":
        # Check for additionalProperties (Dict type)
        additional = field_info.get("additionalProperties")
        if additional:
            # additionalProperties can be True (any value) or a schema dict
            if isinstance(additional, bool):
                # additionalProperties: true means any value type
                return "[String: AnyCodable]"
            value_type = convert_json_schema_to_swift(additional, defs)
            return f"[String: {value_type}]"
        return "AnyCodable"

    return "AnyCodable"


def _schema_to_swift_struct(
    name: str,
    schema: Dict[str, Any],
    defs: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate Swift struct info from JSON schema definition.

    Args:
        name: Struct name
        schema: JSON schema for the type
        defs: Schema definitions for resolving nested $ref

    Returns:
        dict: Swift struct information
    """
    # Apply Swift-safe naming to avoid conflicts with SwiftUI types
    safe_name = get_safe_swift_type_name(name)

    properties = get_schema_properties(schema)
    required = get_schema_required(schema)

    fields = []
    for field_name, field_info in properties.items():
        swift_type = convert_json_schema_to_swift(field_info, defs)

        swift_field_name = to_camel_case(field_name)

        is_optional = field_name not in required
        if is_optional and not swift_type.endswith("?"):
            swift_type = f"{swift_type}?"

        description = field_info.get('description', '')

        fields.append({
            "name": swift_field_name,
            "type": swift_type,
            "json_key": field_name,
            "description": description,
            "is_optional": is_optional,
        })

    return {
        "name": safe_name,
        "fields": fields,
        "doc": schema.get('description', f"{safe_name} struct"),
    }


def pydantic_to_swift(model: Type[BaseModel]) -> Dict[str, Any]:
    """
    Convert Pydantic model to Swift Codable struct definition.

    Args:
        model: Pydantic model class

    Returns:
        dict: Swift struct information with name, fields, and doc

    Example output:
        {
            "name": "TaskStatsParams",
            "fields": [
                {"name": "userId", "type": "String", "json_key": "user_id", "description": "..."},
                ...
            ],
            "doc": "Task statistics parameters"
        }
    """
    if not issubclass(model, BaseModel):
        return {
            "name": "UnknownStruct",
            "fields": [],
            "doc": "",
        }

    try:
        schema = get_model_schema(model)
        properties = get_schema_properties(schema)
        required = get_schema_required(schema)
        defs = get_schema_defs(schema)

        # Apply Swift-safe naming to avoid conflicts with SwiftUI types
        safe_name = get_safe_swift_type_name(model.__name__)

        fields = []
        for field_name, field_info in properties.items():
            swift_type = convert_json_schema_to_swift(field_info, defs)

            # Convert snake_case to camelCase for Swift property names
            swift_field_name = to_camel_case(field_name)

            # Optional for non-required fields
            is_optional = field_name not in required
            if is_optional and not swift_type.endswith("?"):
                swift_type = f"{swift_type}?"

            # Description
            description = field_info.get('description', '')

            fields.append({
                "name": swift_field_name,
                "type": swift_type,
                "json_key": field_name,
                "description": description,
                "is_optional": is_optional,
            })

        doc = model.__doc__ or f"{safe_name} model"

        return {
            "name": safe_name,
            "fields": fields,
            "doc": doc,
        }

    except Exception as e:
        logger.error(f"Failed to convert {model.__name__} to Swift: {e}")
        safe_name = get_safe_swift_type_name(model.__name__)
        return {
            "name": safe_name,
            "fields": [],
            "doc": f"{safe_name} struct",
        }


def pydantic_to_swift_with_nested(model: Type[BaseModel]) -> Dict[str, Any]:
    """
    Convert Pydantic model to Swift Codable struct, including nested types.

    Args:
        model: Pydantic model class

    Returns:
        dict: Contains main struct and any nested structs from $defs
    """
    if not issubclass(model, BaseModel):
        return {
            "main": {"name": "UnknownStruct", "fields": [], "doc": ""},
            "nested": [],
        }

    try:
        schema = get_model_schema(model)
        defs = get_schema_defs(schema)

        # Generate nested structs first
        nested_structs = []
        for def_name, def_schema in defs.items():
            nested_struct = _schema_to_swift_struct(def_name, def_schema, defs)
            nested_structs.append(nested_struct)

        # Generate main struct
        main_struct = pydantic_to_swift(model)

        return {
            "main": main_struct,
            "nested": nested_structs,
        }

    except Exception as e:
        logger.error(f"Failed to convert {model.__name__} to Swift with nested: {e}")
        return {
            "main": {"name": model.__name__, "fields": [], "doc": ""},
            "nested": [],
        }


def _swift_struct_to_string(struct_info: Dict[str, Any]) -> str:
    """
    Convert Swift struct info dict to Swift code string.

    Args:
        struct_info: Dict with name, fields, doc

    Returns:
        str: Swift struct definition
    """
    lines = []

    # Doc comment
    lines.append(f"/// {struct_info['doc']}")
    lines.append(f"public struct {struct_info['name']}: Codable, Sendable {{")

    # Fields
    for field in struct_info['fields']:
        if field['description']:
            lines.append(f"    /// {field['description']}")
        lines.append(f"    public let {field['name']}: {field['type']}")

    # CodingKeys enum if any field has different json_key
    needs_coding_keys = any(
        f['name'] != f['json_key']
        for f in struct_info['fields']
    )

    if needs_coding_keys and struct_info['fields']:
        lines.append("")
        lines.append("    enum CodingKeys: String, CodingKey {")
        for field in struct_info['fields']:
            if field['name'] != field['json_key']:
                lines.append(f"        case {field['name']} = \"{field['json_key']}\"")
            else:
                lines.append(f"        case {field['name']}")
        lines.append("    }")

    lines.append("}")

    return "\n".join(lines)


def generate_swift_types(models: List[Type[BaseModel]]) -> str:
    """
    Generate Swift type definitions for multiple Pydantic models.

    Args:
        models: List of Pydantic model classes

    Returns:
        str: Complete Swift type definitions
    """
    lines = []
    lines.append("// Generated Swift Types")
    lines.append("// Auto-generated from Pydantic models - DO NOT EDIT")
    lines.append("")
    lines.append("import Foundation")
    lines.append("")

    # Track already generated types to avoid duplicates
    generated_types = set()

    for model in models:
        result = pydantic_to_swift_with_nested(model)

        # Generate nested types first
        for nested in result["nested"]:
            if nested["name"] not in generated_types:
                lines.append(_swift_struct_to_string(nested))
                lines.append("")
                generated_types.add(nested["name"])

        # Generate main type
        main = result["main"]
        if main["name"] not in generated_types:
            lines.append(_swift_struct_to_string(main))
            lines.append("")
            generated_types.add(main["name"])

    return "\n".join(lines)
