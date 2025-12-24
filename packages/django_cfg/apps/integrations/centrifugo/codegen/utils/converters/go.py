"""
Go type conversion utilities.

Converts Pydantic models and JSON Schema to Go structs.
"""

import logging
from typing import Any, Dict, Type, List

from pydantic import BaseModel

from .base import get_model_schema, get_schema_properties, get_schema_required

logger = logging.getLogger(__name__)


def convert_json_schema_to_go(field_info: Dict[str, Any]) -> str:
    """
    Convert JSON schema field to Go type.

    Args:
        field_info: JSON schema field information

    Returns:
        str: Go type string

    Examples:
        >>> convert_json_schema_to_go({"type": "string"})
        'string'
        >>> convert_json_schema_to_go({"type": "integer"})
        'int64'
        >>> convert_json_schema_to_go({"type": "array", "items": {"type": "string"}})
        '[]string'
    """
    # Handle anyOf (union types) - Go doesn't have union types, use interface{}
    if "anyOf" in field_info:
        return "interface{}"

    field_type = field_info.get("type", "any")

    type_mapping = {
        "string": "string",
        "integer": "int64",
        "number": "float64",
        "boolean": "bool",
        "null": "interface{}",
    }

    if field_type in type_mapping:
        return type_mapping[field_type]

    if field_type == "array":
        items = field_info.get("items", {})
        item_type = convert_json_schema_to_go(items)
        return f"[]{item_type}"

    if field_type == "object":
        return "map[string]interface{}"

    return "interface{}"


def pydantic_to_go(model: Type[BaseModel]) -> Dict[str, Any]:
    """
    Convert Pydantic model to Go struct definition.

    Args:
        model: Pydantic model class

    Returns:
        dict: Go struct information with name, fields, and doc
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

        fields = []
        for field_name, field_info in properties.items():
            go_type = convert_json_schema_to_go(field_info)

            # Convert snake_case to PascalCase for Go field names
            go_field_name = ''.join(word.capitalize() for word in field_name.split('_'))

            # Pointer types for optional fields
            is_optional = field_name not in required
            if is_optional and go_type not in ["interface{}", "map[string]interface{}"]:
                go_type = f"*{go_type}"

            # JSON tag
            json_tag = f'`json:"{field_name}"`'

            # Description
            description = field_info.get('description', '')

            fields.append({
                "name": go_field_name,
                "type": go_type,
                "json_tag": json_tag,
                "description": description,
            })

        doc = model.__doc__ or f"{model.__name__} struct"

        return {
            "name": model.__name__,
            "fields": fields,
            "doc": doc,
        }

    except Exception as e:
        logger.error(f"Failed to convert {model.__name__} to Go: {e}")
        return {
            "name": model.__name__,
            "fields": [],
            "doc": f"{model.__name__} struct",
        }


def generate_go_types(models: List[Type[BaseModel]]) -> str:
    """
    Generate Go type definitions for multiple Pydantic models.

    Args:
        models: List of Pydantic model classes

    Returns:
        str: Complete Go type definitions
    """
    lines = []
    lines.append("// Generated Go Types")
    lines.append("// Auto-generated from Pydantic models - DO NOT EDIT")
    lines.append("")

    for model in models:
        struct_info = pydantic_to_go(model)

        # Add doc comment
        lines.append(f"// {struct_info['doc']}")
        lines.append(f"type {struct_info['name']} struct {{")

        for field in struct_info['fields']:
            if field['description']:
                lines.append(f"\t// {field['description']}")
            lines.append(f"\t{field['name']} {field['type']} {field['json_tag']}")

        lines.append("}")
        lines.append("")

    return "\n".join(lines)
