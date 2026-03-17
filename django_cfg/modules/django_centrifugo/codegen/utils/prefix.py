"""
Shared prefix utilities for Centrifugo type generation.

All Centrifugo types are prefixed with 'Ws' to avoid naming conflicts
with REST API types that may have the same names (e.g., FileChange, FileEntry).

Usage:
    from ...utils.prefix import WS_TYPE_PREFIX, add_prefix_to_type_data

    # Prefix a single type name
    prefixed = add_prefix_to_type_name("FileEntry")  # -> "WsFileEntry"

    # Prefix type data dict (name + field type references)
    type_data = {"name": "Event", "fields": [{"type": "FileEntry"}]}
    prefixed_data = add_prefix_to_type_data(type_data, {"FileEntry", "Event"})
"""

import re
from typing import Dict, List, Set, Any

# Type prefix for Centrifugo types to avoid conflicts with REST API types
WS_TYPE_PREFIX = "Ws"


def add_prefix_to_type_name(type_name: str) -> str:
    """
    Add Ws prefix to a type name.

    Args:
        type_name: Original type name (e.g., "FileEntry")

    Returns:
        Prefixed type name (e.g., "WsFileEntry")
    """
    return f"{WS_TYPE_PREFIX}{type_name}"


def add_prefix_to_field_types(
    field_type: str,
    all_type_names: Set[str],
    prefix: str = WS_TYPE_PREFIX,
) -> str:
    """
    Update type references in a field type string.

    Handles various type formats:
    - Simple: "FileEntry" -> "WsFileEntry"
    - Optional: "FileEntry?" -> "WsFileEntry?"
    - Array: "[FileEntry]" -> "[WsFileEntry]"
    - Generic: "List[FileEntry]" -> "List[WsFileEntry]"
    - Nested: "Dict[str, FileEntry]" -> "Dict[str, WsFileEntry]"

    Args:
        field_type: The field type string to update
        all_type_names: Set of all type names that need prefixing
        prefix: The prefix to add (default: "Ws")

    Returns:
        Updated field type string with prefixed references
    """
    result = field_type
    for type_name in all_type_names:
        # Match whole word only (not partial matches)
        # Handles: TypeName, TypeName?, [TypeName], [TypeName]?, List[TypeName], etc.
        result = re.sub(
            rf'\b{re.escape(type_name)}\b',
            f'{prefix}{type_name}',
            result
        )
    return result


def add_prefix_to_type_data(
    type_data: Dict[str, Any],
    all_type_names: Set[str],
    prefix: str = WS_TYPE_PREFIX,
    field_type_keys: List[str] = None,
) -> Dict[str, Any]:
    """
    Add prefix to type name and update all type references in fields.

    This function:
    1. Prefixes the type name itself
    2. Updates all field type references to use prefixed versions

    Args:
        type_data: Dict with at least 'name' key, optionally 'fields'
        all_type_names: Set of all type names that need prefixing
        prefix: The prefix to add (default: "Ws")
        field_type_keys: List of keys in field dicts that contain type info
                        (default: ["type", "swift_type", "go_type", "ts_type", "py_type"])

    Returns:
        Updated type_data dict with prefixed names and references

    Example:
        >>> type_data = {
        ...     "name": "FileCreatedEvent",
        ...     "fields": [
        ...         {"name": "item", "type": "FileChangeItem"},
        ...         {"name": "path", "type": "String"},
        ...     ]
        ... }
        >>> all_types = {"FileCreatedEvent", "FileChangeItem"}
        >>> result = add_prefix_to_type_data(type_data, all_types)
        >>> result["name"]
        'WsFileCreatedEvent'
        >>> result["fields"][0]["type"]
        'WsFileChangeItem'
    """
    if field_type_keys is None:
        field_type_keys = ["type", "swift_type", "go_type", "ts_type", "py_type"]

    result = type_data.copy()
    result["name"] = f"{prefix}{type_data['name']}"

    # Update field type references
    if "fields" in result:
        updated_fields = []
        for field in result["fields"]:
            updated_field = field.copy()
            for key in field_type_keys:
                if key in updated_field:
                    updated_field[key] = add_prefix_to_field_types(
                        updated_field[key],
                        all_type_names,
                        prefix,
                    )
            updated_fields.append(updated_field)
        result["fields"] = updated_fields

    return result


def collect_type_names_from_models(
    models: list,
    get_nested_types: callable = None,
) -> Set[str]:
    """
    Collect all type names from a list of models (including nested types).

    Args:
        models: List of Pydantic models or similar
        get_nested_types: Optional function to extract nested types from each model.
                         Should return a list of type dicts with 'name' key.

    Returns:
        Set of all type names found
    """
    all_names = set()
    for model in models:
        if hasattr(model, '__name__'):
            all_names.add(model.__name__)
        if get_nested_types:
            for nested in get_nested_types(model):
                if isinstance(nested, dict) and 'name' in nested:
                    all_names.add(nested['name'])
    return all_names


__all__ = [
    "WS_TYPE_PREFIX",
    "add_prefix_to_type_name",
    "add_prefix_to_field_types",
    "add_prefix_to_type_data",
    "collect_type_names_from_models",
]
