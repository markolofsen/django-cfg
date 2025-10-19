"""
Auto-fix enum naming collisions in OpenAPI schema.

This postprocessing hook automatically generates unique, descriptive enum names
based on model names to avoid collisions like "Status50eEnum", "StatusA98Enum".

Instead generates: "ProductStatusEnum", "OrderStatusEnum", "PostStatusEnum", etc.
"""

import logging
import re
from typing import Any, Dict

logger = logging.getLogger(__name__)


def auto_fix_enum_names(result: Dict[str, Any], generator, request, public) -> Dict[str, Any]:
    """
    DRF Spectacular postprocessing hook to auto-fix enum naming collisions.

    Automatically detects and fixes enum naming collisions by using model names.

    Args:
        result: OpenAPI schema dict
        generator: Schema generator instance
        request: HTTP request
        public: Whether schema is public

    Returns:
        Modified OpenAPI schema with fixed enum names

    Example:
        Before: Status50eEnum, StatusA98Enum (collision hashes)
        After:  ProductStatusEnum, OrderStatusEnum (descriptive names)
    """

    if 'components' not in result or 'schemas' not in result['components']:
        return result

    schemas = result['components']['schemas']

    # Track enum references and their sources (model + field)
    enum_sources: Dict[str, list] = {}  # enum_name -> [(model_name, field_name, choices)]
    enum_renames: Dict[str, str] = {}   # old_name -> new_name

    # Step 1: Find all enums and their sources
    for schema_name, schema in schemas.items():
        if schema.get('type') == 'object' and 'properties' in schema:
            # This is a model schema
            model_name = _extract_model_name(schema_name)

            for field_name, field_schema in schema['properties'].items():
                # Check if field references an enum
                if '$ref' in field_schema:
                    enum_ref = field_schema['$ref']
                    if '#/components/schemas/' in enum_ref:
                        enum_name = enum_ref.split('/')[-1]

                        # Track enum source
                        if enum_name not in enum_sources:
                            enum_sources[enum_name] = []

                        enum_sources[enum_name].append((model_name, field_name))

    # Step 2: Detect collisions and generate better names
    for enum_name, sources in enum_sources.items():
        # Check if enum looks like a collision (contains hash or generic name)
        if _is_collision_enum(enum_name):
            # Multiple models use this enum - need unique names
            if len(sources) == 1:
                # Single source - generate descriptive name
                model_name, field_name = sources[0]
                new_name = _generate_enum_name(model_name, field_name)
                enum_renames[enum_name] = new_name

                logger.debug(f"  Renaming {enum_name} -> {new_name} (from {model_name}.{field_name})")

    # Step 3: Apply renames to schema
    if enum_renames:
        logger.info(f"🔧 Auto-fixed {len(enum_renames)} enum naming collision(s)")
        _apply_enum_renames(result, enum_renames)

    return result


def _extract_model_name(schema_name: str) -> str:
    """
    Extract model name from schema name.

    Examples:
        "Product" -> "Product"
        "ProductDetail" -> "Product"
        "PaginatedProductList" -> "Product"
    """
    # Remove common prefixes/suffixes
    name = schema_name

    # Remove pagination wrapper
    if name.startswith('Paginated') and name.endswith('List'):
        name = name[9:-4]  # Remove "Paginated" and "List"

    # Remove common suffixes
    for suffix in ['Serializer', 'Detail', 'List', 'Create', 'Update']:
        if name.endswith(suffix):
            name = name[:-len(suffix)]
            break

    return name


def _is_collision_enum(enum_name: str) -> bool:
    """
    Check if enum name looks like a collision (contains hash).

    Examples:
        "Status50eEnum" -> True (has hash)
        "StatusA98Enum" -> True (has hash)
        "ProductStatusEnum" -> False (descriptive)
    """
    # Check if enum contains hash-like patterns (3+ hex chars)
    if re.search(r'[0-9A-Fa-f]{3,}Enum$', enum_name):
        return True

    # Check for generic single-word enums that are likely collisions
    # (e.g., "StatusEnum" without model prefix)
    if re.match(r'^[A-Z][a-z]+Enum$', enum_name):
        # Single word + Enum - likely collision
        return True

    return False


def _generate_enum_name(model_name: str, field_name: str) -> str:
    """
    Generate descriptive enum name from model and field.

    Examples:
        ("Product", "status") -> "ProductStatusEnum"
        ("Order", "status") -> "OrderStatusEnum"
        ("Post", "status") -> "PostStatusEnum"
    """
    # Capitalize field name
    field_capitalized = field_name.capitalize()

    # Combine: ModelName + FieldName + Enum
    return f"{model_name}{field_capitalized}Enum"


def _apply_enum_renames(schema: Dict[str, Any], renames: Dict[str, str]) -> None:
    """
    Apply enum renames throughout the schema.

    Renames both:
    1. Schema component definitions (components/schemas/OldName -> NewName)
    2. All references to renamed enums ($ref: #/components/schemas/OldName)
    """
    if 'components' not in schema or 'schemas' not in schema['components']:
        return

    schemas = schema['components']['schemas']

    # Step 1: Rename schema definitions
    for old_name, new_name in renames.items():
        if old_name in schemas:
            schemas[new_name] = schemas.pop(old_name)
            logger.debug(f"  Renamed schema: {old_name} -> {new_name}")

    # Step 2: Update all $ref references
    _update_refs_recursive(schema, renames)


def _update_refs_recursive(obj: Any, renames: Dict[str, str]) -> None:
    """
    Recursively update all $ref references in schema.
    """
    if isinstance(obj, dict):
        # Check if this dict contains a $ref
        if '$ref' in obj:
            ref = obj['$ref']
            if '#/components/schemas/' in ref:
                enum_name = ref.split('/')[-1]
                if enum_name in renames:
                    obj['$ref'] = f"#/components/schemas/{renames[enum_name]}"

        # Recurse into dict values
        for value in obj.values():
            _update_refs_recursive(value, renames)

    elif isinstance(obj, list):
        # Recurse into list items
        for item in obj:
            _update_refs_recursive(item, renames)
