"""
Shared Utilities for Django Client Generator.

Common naming conventions, string transformations, etc.
"""

from .naming import (
    to_camel_case,
    to_pascal_case,
    to_snake_case,
    header_to_param_name,
)

__all__ = [
    "to_camel_case",
    "to_pascal_case",
    "to_snake_case",
    "header_to_param_name",
]
