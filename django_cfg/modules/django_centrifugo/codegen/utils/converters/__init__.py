"""
Type converters for code generation.

This module provides type conversion utilities for generating code in different
programming languages from Pydantic models.

Supported languages:
- TypeScript
- Python
- Go
- Swift
"""

# TypeScript
from .typescript import (
    convert_json_schema_to_typescript,
    pydantic_to_typescript,
    generate_typescript_types,
    # Enum support
    is_int_enum,
    int_enum_to_typescript,
    generate_typescript_enums,
)

# Python
from .python import (
    convert_json_schema_to_python,
    pydantic_to_python,
    generate_python_types,
)

# Go
from .go import (
    convert_json_schema_to_go,
    pydantic_to_go,
    generate_go_types,
)

# Swift
from .swift import (
    convert_json_schema_to_swift,
    pydantic_to_swift,
    pydantic_to_swift_with_nested,
    generate_swift_types,
    # Enum support
    is_int_enum as is_int_enum_swift,
    int_enum_to_swift,
    generate_swift_enums,
)

__all__ = [
    # TypeScript
    "convert_json_schema_to_typescript",
    "pydantic_to_typescript",
    "generate_typescript_types",
    "is_int_enum",
    "int_enum_to_typescript",
    "generate_typescript_enums",
    # Python
    "convert_json_schema_to_python",
    "pydantic_to_python",
    "generate_python_types",
    # Go
    "convert_json_schema_to_go",
    "pydantic_to_go",
    "generate_go_types",
    # Swift
    "convert_json_schema_to_swift",
    "pydantic_to_swift",
    "pydantic_to_swift_with_nested",
    "generate_swift_types",
    "is_int_enum_swift",
    "int_enum_to_swift",
    "generate_swift_enums",
]
