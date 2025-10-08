"""
Universal Parser - OpenAPI → IR conversion.

This package provides parsers for converting OpenAPI specifications
(both 3.0.3 and 3.1.0) to the unified IR (Intermediate Representation).

Usage:
    >>> from django_cfg.modules.django_client.core.parser import parse_openapi
    >>> spec_dict = {...}  # OpenAPI spec as dict
    >>> context = parse_openapi(spec_dict)
    >>> context.openapi_info.version
    '3.1.0'
    >>> context.schemas['User']
    IRSchemaObject(name='User', ...)

Auto-detection:
    The parse_openapi() function automatically detects the OpenAPI version
    and uses the appropriate parser (OpenAPI30Parser or OpenAPI31Parser).
"""

from typing import Any

from django_cfg.modules.django_client.core.ir import IRContext
from django_cfg.modules.django_client.core.parser.models import OpenAPISpec
from django_cfg.modules.django_client.core.parser.openapi30 import OpenAPI30Parser
from django_cfg.modules.django_client.core.parser.openapi31 import OpenAPI31Parser

__all__ = [
    "parse_openapi",
    "OpenAPI30Parser",
    "OpenAPI31Parser",
]


def parse_openapi(spec_dict: dict[str, Any]) -> IRContext:
    """
    Parse OpenAPI specification to IR (auto-detects version).

    This is the main entry point for parsing OpenAPI specs. It automatically
    detects the OpenAPI version and uses the appropriate parser.

    Args:
        spec_dict: OpenAPI spec as dictionary (from JSON/YAML)

    Returns:
        IRContext with all schemas and operations

    Raises:
        ValueError: If OpenAPI version is unsupported or COMPONENT_SPLIT_REQUEST not detected

    Examples:
        >>> spec = {
        ...     "openapi": "3.1.0",
        ...     "info": {"title": "My API", "version": "1.0.0"},
        ...     "paths": {...},
        ...     "components": {"schemas": {...}},
        ... }
        >>> context = parse_openapi(spec)
        >>> context.has_request_response_split
        True
    """
    # Validate and parse spec
    spec = OpenAPISpec.model_validate(spec_dict)

    # Select parser based on version
    if spec.is_openapi_30:
        parser = OpenAPI30Parser(spec)
    elif spec.is_openapi_31:
        parser = OpenAPI31Parser(spec)
    else:
        raise ValueError(f"Unsupported OpenAPI version: {spec.openapi}")

    # Parse to IR
    return parser.parse()
