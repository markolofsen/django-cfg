"""
OpenAPI 3.0.3 Parser - Handles nullable: true.

This parser handles OpenAPI 3.0.x specifications which use the proprietary
`nullable: true` extension for nullable fields.

Reference: https://swagger.io/docs/specification/data-models/data-types/#null
"""

from .base import BaseParser
from .models import SchemaObject


class OpenAPI30Parser(BaseParser):
    """
    Parser for OpenAPI 3.0.x specifications.

    Key differences from 3.1.0:
    - Uses nullable: true (proprietary extension)
    - exclusiveMinimum/exclusiveMaximum are booleans (not numbers)
    - No const keyword
    - No contentMediaType/contentEncoding

    Examples:
        >>> from django_cfg.modules.django_client.core.parser.models import OpenAPISpec
        >>> spec_dict = {...}  # OAS 3.0.3 spec
        >>> spec = OpenAPISpec.model_validate(spec_dict)
        >>> parser = OpenAPI30Parser(spec)
        >>> context = parser.parse()
        >>> context.openapi_info.version
        '3.0.3'
    """

    def _detect_nullable(self, schema: SchemaObject) -> bool:
        """
        Detect if schema is nullable using OAS 3.0.3 style.

        In OpenAPI 3.0.x, nullable is indicated by:
            nullable: true

        Examples:
            >>> schema = SchemaObject(type='string', nullable=True)
            >>> parser._detect_nullable(schema)
            True

            >>> schema = SchemaObject(type='string')
            >>> parser._detect_nullable(schema)
            False

        Args:
            schema: Raw SchemaObject from spec

        Returns:
            True if nullable, False otherwise
        """
        return schema.is_nullable_30
