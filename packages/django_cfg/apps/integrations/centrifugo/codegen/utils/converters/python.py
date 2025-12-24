"""
Python type conversion utilities.

Converts Pydantic models and JSON Schema to Python type hints.
"""

import logging
from typing import Any, Dict, Type, List

from pydantic import BaseModel

from .base import get_model_schema, get_schema_properties, get_schema_required

logger = logging.getLogger(__name__)


def convert_json_schema_to_python(field_info: Dict[str, Any]) -> str:
    """
    Convert JSON schema field to Python type.

    Args:
        field_info: JSON schema field information

    Returns:
        str: Python type string

    Examples:
        >>> convert_json_schema_to_python({"type": "string"})
        'str'
        >>> convert_json_schema_to_python({"type": "array", "items": {"type": "string"}})
        'List[str]'
    """
    field_type = field_info.get("type", "any")

    type_mapping = {
        "string": "str",
        "integer": "int",
        "number": "float",
        "boolean": "bool",
        "null": "None",
    }

    if field_type in type_mapping:
        return type_mapping[field_type]

    if field_type == "array":
        items = field_info.get("items", {})
        item_type = convert_json_schema_to_python(items)
        return f"List[{item_type}]"

    if field_type == "object":
        return "Dict[str, Any]"

    return "Any"


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
        schema = get_model_schema(model)
        properties = get_schema_properties(schema)
        required = get_schema_required(schema)

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
