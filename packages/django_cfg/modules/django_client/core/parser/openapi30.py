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
            anyOf: [{"type": "string"}, {"type": "null"}]  # Pydantic style

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
        # Check standard nullable: true format
        if schema.is_nullable_30:
            return True

        # Check anyOf: [{"type": "X"}, {"type": "null"}] format (Pydantic)
        # or anyOf: [{"$ref": "..."}, {"type": "null"}] format
        if schema.anyOf and len(schema.anyOf) == 2:
            has_null = False
            has_actual_type = False

            for item in schema.anyOf:
                if not isinstance(item, SchemaObject):
                    continue

                if item.base_type == 'null':
                    has_null = True
                elif item.base_type or item.ref:
                    # Has actual type (either base_type or $ref)
                    has_actual_type = True

            # If one is null and another is actual type, it's nullable
            if has_null and has_actual_type:
                return True

        return False
