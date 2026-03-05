"""
OpenAPI Modern Parser - Handles type: ['string', 'null'].

Parser for OpenAPI 3.1.0+ specifications (3.1.x, 3.2.x) which use
JSON Schema 2020-12 standard for nullable fields (type arrays with 'null').

References:
    https://spec.openapis.org/oas/v3.1.0
    https://spec.openapis.org/oas/v3.2.0
"""

from .base import BaseParser
from .models import ReferenceObject, SchemaObject


class OpenAPIModernParser(BaseParser):
    """
    Parser for OpenAPI 3.1.0+ specifications (3.1.x, 3.2.x).

    Both 3.1.x and 3.2.x use JSON Schema Draft 2020-12. The ``nullable: true``
    keyword was removed in 3.2.0, but the type-array style is identical.

    Key differences from 3.0.x:
    - Uses type: ['string', 'null'] (JSON Schema standard)
    - exclusiveMinimum/exclusiveMaximum are numbers (not booleans)
    - Supports const keyword
    - Supports contentMediaType/contentEncoding
    - Supports $schema and $vocabulary
    - Aligned with JSON Schema 2020-12

    Examples:
        >>> from django_cfg.modules.django_client.core.parser.models import OpenAPISpec
        >>> spec_dict = {...}  # OAS 3.1.0 or 3.2.0 spec
        >>> spec = OpenAPISpec.model_validate(spec_dict)
        >>> parser = OpenAPIModernParser(spec)
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
            anyOf: [{"type": "string"}, {"type": "null"}]  # Pydantic style
            etc.

        Also handles OAS 3.0.3-style ``nullable: true`` as a fallback, since
        tools like drf-spectacular may emit ``nullable: true`` in custom schemas
        (e.g. pagination) even when the spec version is 3.1.0.

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

            >>> schema = SchemaObject(type='integer', nullable=True)
            >>> parser._detect_nullable(schema)
            True

        Args:
            schema: Raw SchemaObject from spec

        Returns:
            True if nullable, False otherwise
        """
        # Check standard type: ['string', 'null'] format
        if schema.is_nullable_31:
            return True

        # Fallback: check OAS 3.0.3-style nullable: true
        # drf-spectacular custom schemas (e.g. pagination) may use this
        # even in a 3.1.0 spec
        if schema.is_nullable_30:
            return True

        # Check anyOf/oneOf: [{"type": "X"}, {"type": "null"}] format
        # or anyOf/oneOf: [{"$ref": "..."}, {"type": "null"}] format
        # drf-spectacular uses oneOf for @extend_schema_field(Serializer(allow_null=True))
        for combinator in (schema.anyOf, schema.oneOf):
            if combinator and len(combinator) == 2:
                has_null = False
                has_actual_type = False

                for item in combinator:
                    if isinstance(item, SchemaObject):
                        if item.base_type == 'null':
                            has_null = True
                        elif item.base_type:
                            has_actual_type = True
                    elif isinstance(item, ReferenceObject):
                        # $ref counts as actual type
                        has_actual_type = True

                if has_null and has_actual_type:
                    return True

        return False
