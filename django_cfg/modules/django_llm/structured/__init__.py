"""
Structured output — response format helpers and JSON extraction.
"""

from .enum_coercion import EnumCoercer
from .extractor import JSONExtractor
from .response_format import (
    ResponseFormat,
    build_response_format,
    to_strict_json_schema,
    wants_json,
)

__all__ = [
    'EnumCoercer',
    'JSONExtractor',
    'ResponseFormat',
    'build_response_format',
    'to_strict_json_schema',
    'wants_json',
]
