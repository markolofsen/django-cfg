"""
Smart Field Detection for Django Client Generator.

Infers field semantics from naming conventions and OpenAPI metadata.
"""

from .field_detector import (
    FieldMeta,
    InputType,
    ValidationRule,
    detect_field_meta,
    get_default_input_type,
)

__all__ = [
    "FieldMeta",
    "InputType",
    "ValidationRule",
    "detect_field_meta",
    "get_default_input_type",
]
