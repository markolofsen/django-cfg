"""
Utilities for code generation.
"""

from .naming import (
    SWIFT_RESERVED_TYPES,
    get_safe_swift_type_name,
    is_swift_reserved_type,
    sanitize_method_name,
    to_camel_case,
    to_pascal_case,
    to_python_method_name,
    to_typescript_method_name,
    to_go_method_name,
    to_swift_method_name,
    to_swift_field_name,
)

# Import from new converters module structure
from .converters import (
    # TypeScript
    convert_json_schema_to_typescript,
    pydantic_to_typescript,
    generate_typescript_types,
    is_int_enum,
    int_enum_to_typescript,
    generate_typescript_enums,
    # Python
    convert_json_schema_to_python,
    pydantic_to_python,
    generate_python_types,
    # Go
    convert_json_schema_to_go,
    pydantic_to_go,
    generate_go_types,
    # Swift
    convert_json_schema_to_swift,
    pydantic_to_swift,
    pydantic_to_swift_with_nested,
    generate_swift_types,
)

__all__ = [
    # Naming
    "SWIFT_RESERVED_TYPES",
    "get_safe_swift_type_name",
    "is_swift_reserved_type",
    "sanitize_method_name",
    "to_camel_case",
    "to_pascal_case",
    "to_python_method_name",
    "to_typescript_method_name",
    "to_go_method_name",
    "to_swift_method_name",
    "to_swift_field_name",
    # TypeScript converters
    "convert_json_schema_to_typescript",
    "pydantic_to_typescript",
    "generate_typescript_types",
    "is_int_enum",
    "int_enum_to_typescript",
    "generate_typescript_enums",
    # Python converters
    "convert_json_schema_to_python",
    "pydantic_to_python",
    "generate_python_types",
    # Go converters
    "convert_json_schema_to_go",
    "pydantic_to_go",
    "generate_go_types",
    # Swift converters
    "convert_json_schema_to_swift",
    "pydantic_to_swift",
    "pydantic_to_swift_with_nested",
    "generate_swift_types",
]
