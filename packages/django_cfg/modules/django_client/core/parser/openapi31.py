"""
OpenAPI 3.1.0 Parser - Handles type: ['string', 'null'].

This parser handles OpenAPI 3.1.0 specifications which use JSON Schema 2020-12
standard for nullable fields (type arrays with 'null').

Reference: https://spec.openapis.org/oas/v3.1.0
"""

from .base import BaseParser
from .models import SchemaObject


class OpenAPI31Parser(BaseParser):
    """
    Parser for OpenAPI 3.1.0 specifications.

    Key differences from 3.0.x:
    - Uses type: ['string', 'null'] (JSON Schema standard)
    - exclusiveMinimum/exclusiveMaximum are numbers (not booleans)
    - Supports const keyword
    - Supports contentMediaType/contentEncoding
    - Supports $schema and $vocabulary
    - Aligned with JSON Schema 2020-12

    Examples:
        >>> from django_cfg.modules.django_client.core.parser.models import OpenAPISpec
        >>> spec_dict = {...}  # OAS 3.1.0 spec
        >>> spec = OpenAPISpec.model_validate(spec_dict)
        >>> parser = OpenAPI31Parser(spec)
        >>> context = parser.parse()
        >>> context.openapi_info.version
        '3.1.0'
    """

    def _detect_nullable(self, schema: SchemaObject) -> bool:
        """
        Detect if schema is nullable using OAS 3.1.0 style.

        In OpenAPI 3.1.0, nullable is indicated by:
            type: ['string', 'null']
            type: ['integer', 'null']
            etc.

        Examples:
            >>> schema = SchemaObject(type=['string', 'null'])
            >>> parser._detect_nullable(schema)
            True

            >>> schema = SchemaObject(type='string')
            >>> parser._detect_nullable(schema)
            False

            >>> schema = SchemaObject(type=['integer', 'null'])
            >>> parser._detect_nullable(schema)
            True

        Args:
            schema: Raw SchemaObject from spec

        Returns:
            True if nullable, False otherwise
        """
        return schema.is_nullable_31
