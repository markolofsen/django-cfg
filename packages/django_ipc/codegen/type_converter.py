"""
Type conversion utilities for code generation.

Converts Pydantic models to TypeScript interfaces and Python type hints.
Adapted from unrealon-openapi/generators/common/utils.py
"""

import logging
from typing import Any, Dict, Type, List, get_args, get_origin
from pydantic import BaseModel

logger = logging.getLogger(__name__)


def convert_json_schema_to_typescript(field_info: Dict[str, Any]) -> str:
    """
    Convert JSON schema field to TypeScript type.

    Args:
        field_info: JSON schema field information

    Returns:
        str: TypeScript type string
    """
    # Handle anyOf (union types)
    if "anyOf" in field_info:
        types = [convert_json_schema_to_typescript(t) for t in field_info["anyOf"]]
        return " | ".join(types)

    field_type = field_info.get("type", "any")

    if field_type == "string":
        return "string"
    elif field_type == "integer":
        return "number"
    elif field_type == "number":
        return "number"
    elif field_type == "boolean":
        return "boolean"
    elif field_type == "array":
        items = field_info.get("items", {})
        item_type = convert_json_schema_to_typescript(items)
        return f"{item_type}[]"
    elif field_type == "object":
        return "Record<string, any>"
    elif field_type == "null":
        return "null"
    else:
        return "any"


def convert_json_schema_to_python(field_info: Dict[str, Any]) -> str:
    """
    Convert JSON schema field to Python type.

    Args:
        field_info: JSON schema field information

    Returns:
        str: Python type string
    """
    field_type = field_info.get("type", "any")

    if field_type == "string":
        return "str"
    elif field_type == "integer":
        return "int"
    elif field_type == "number":
        return "float"
    elif field_type == "boolean":
        return "bool"
    elif field_type == "array":
        items = field_info.get("items", {})
        item_type = convert_json_schema_to_python(items)
        return f"List[{item_type}]"
    elif field_type == "object":
        return "Dict[str, Any]"
    elif field_type == "null":
        return "None"
    else:
        return "Any"


def pydantic_to_typescript(model: Type[BaseModel]) -> str:
    """
    Convert Pydantic model to TypeScript interface.

    Args:
        model: Pydantic model class

    Returns:
        str: TypeScript interface definition
    """
    if not issubclass(model, BaseModel):
        return "any"

    try:
        schema = model.model_json_schema()
        properties = schema.get('properties', {})
        required = schema.get('required', [])

        ts_fields = []
        for field_name, field_info in properties.items():
            ts_type = convert_json_schema_to_typescript(field_info)
            optional = '?' if field_name not in required else ''

            # Add description as comment if available
            description = field_info.get('description')
            if description:
                ts_fields.append(f"  /** {description} */")

            ts_fields.append(f"  {field_name}{optional}: {ts_type};")

        interface_code = f"export interface {model.__name__} {{\n"
        interface_code += "\n".join(ts_fields)
        interface_code += "\n}"

        return interface_code

    except Exception as e:
        logger.error(f"Failed to convert {model.__name__} to TypeScript: {e}")
        return f"export interface {model.__name__} {{ [key: string]: any; }}"


def pydantic_to_python(model: Type[BaseModel]) -> str:
    """
    Convert Pydantic model to Python class definition.

    Args:
        model: Pydantic model class

    Returns:
        str: Python class definition
    """
    if not issubclass(model, BaseModel):
        return "Any"

    try:
        schema = model.model_json_schema()
        properties = schema.get('properties', {})
        required = schema.get('required', [])

        py_fields = []
        for field_name, field_info in properties.items():
            py_type = convert_json_schema_to_python(field_info)

            # Add description as docstring comment
            description = field_info.get('description')
            if description:
                py_fields.append(f'    """{description}"""')

            if field_name in required:
                py_fields.append(f"    {field_name}: {py_type}")
            else:
                py_fields.append(f"    {field_name}: Optional[{py_type}] = None")

        doc = model.__doc__ or f"{model.__name__} model"

        class_code = f"class {model.__name__}(BaseModel):\n"
        class_code += f'    """{doc}"""\n\n'
        class_code += "\n".join(py_fields) if py_fields else "    pass"

        return class_code

    except Exception as e:
        logger.error(f"Failed to convert {model.__name__} to Python: {e}")
        return f"class {model.__name__}(BaseModel):\n    pass"


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


def generate_python_types(models: List[Type[BaseModel]]) -> str:
    """
    Generate Python type definitions for multiple Pydantic models.

    Args:
        models: List of Pydantic model classes

    Returns:
        str: Complete Python type definitions
    """
    lines = []
    lines.append('"""Generated Python Types"""')
    lines.append('"""Auto-generated from Pydantic models - DO NOT EDIT"""')
    lines.append("")
    lines.append("from typing import Optional, List, Dict, Any")
    lines.append("from pydantic import BaseModel")
    lines.append("")

    for model in models:
        class_def = pydantic_to_python(model)
        lines.append(class_def)
        lines.append("")

    return "\n".join(lines)
