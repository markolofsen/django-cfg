"""
Base utilities for type conversion.

Common functions and types used by language-specific converters.
"""

import logging
from typing import Any, Dict, List, Type, Set

from pydantic import BaseModel

logger = logging.getLogger(__name__)


def get_model_schema(model: Type[BaseModel]) -> Dict[str, Any]:
    """
    Get JSON schema from Pydantic model.

    Args:
        model: Pydantic model class

    Returns:
        JSON schema dictionary
    """
    return model.model_json_schema()


def get_schema_properties(schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get properties from JSON schema.

    Args:
        schema: JSON schema dictionary

    Returns:
        Properties dictionary
    """
    return schema.get("properties", {})


def get_schema_required(schema: Dict[str, Any]) -> Set[str]:
    """
    Get required fields from JSON schema.

    Args:
        schema: JSON schema dictionary

    Returns:
        Set of required field names
    """
    required = schema.get("required", [])
    # Handle case where required is a boolean (some JSON schema variants)
    if isinstance(required, bool):
        # If required=True, all properties are required
        if required:
            return set(schema.get("properties", {}).keys())
        return set()
    return set(required)


def get_schema_defs(schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get $defs (definitions) from JSON schema.

    Args:
        schema: JSON schema dictionary

    Returns:
        Definitions dictionary
    """
    return schema.get("$defs", {})


def extract_ref_name(ref: str) -> str:
    """
    Extract type name from $ref.

    Args:
        ref: Reference string like "#/$defs/TypeName"

    Returns:
        Type name
    """
    if ref.startswith("#/$defs/"):
        return ref.split("/")[-1]
    return ref.split("/")[-1]


def is_optional_anyof(field_info: Dict[str, Any]) -> tuple[bool, Dict[str, Any] | None]:
    """
    Check if anyOf represents an Optional type (type | null).

    Args:
        field_info: Field info with anyOf

    Returns:
        Tuple of (is_optional, non_null_type_info)
    """
    if "anyOf" not in field_info:
        return False, None

    types = field_info["anyOf"]
    non_null_types = [t for t in types if t.get("type") != "null"]
    has_null = len(non_null_types) < len(types)

    if has_null and len(non_null_types) == 1:
        return True, non_null_types[0]

    return False, None


def collect_models_from_methods(methods: List[Any]) -> List[Type[BaseModel]]:
    """
    Collect unique models from RPC methods.

    Args:
        methods: List of RPCMethodInfo objects

    Returns:
        List of unique Pydantic model classes
    """
    models = set()
    for method in methods:
        if hasattr(method, "param_type") and method.param_type:
            models.add(method.param_type)
        if hasattr(method, "return_type") and method.return_type:
            models.add(method.return_type)
    return list(models)
