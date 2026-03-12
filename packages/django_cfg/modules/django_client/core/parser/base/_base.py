"""
BaseParser — abstract OpenAPI → IR parser assembled from focused mixins.

Version-specific logic (nullable detection) lives in subclasses:
- OpenAPI30Parser  — nullable: true  (OAS 3.0.x)
- OpenAPIModernParser — type: ['X', 'null']  (OAS 3.1.x / 3.2.x)
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..models import OpenAPISpec, SchemaObject
from ...ir import IRContext, IRSchemaObject

from ._metadata import MetadataParserMixin
from ._schema_validator import SchemaValidatorMixin
from ._schema_parser import SchemaParserMixin
from ._operation_parser import OperationParserMixin
from ._body_validator import RequestBodyValidatorMixin


class BaseParser(
    MetadataParserMixin,
    SchemaValidatorMixin,
    SchemaParserMixin,
    OperationParserMixin,
    RequestBodyValidatorMixin,
    ABC,
):
    """
    Abstract base parser for OpenAPI → IR conversion.

    Subclasses implement:
    - _detect_nullable(schema) — version-specific nullable detection
    """

    def __init__(self, spec: OpenAPISpec) -> None:
        self.spec = spec
        self._schema_cache: dict[str, IRSchemaObject] = {}
        self._inline_schemas: dict[str, IRSchemaObject] = {}
        self._enum_id_to_name: dict[str, str] = {}

    def parse(self) -> IRContext:
        """
        Parse OpenAPI spec to IRContext.

        Raises:
            ValueError: On schema name conflicts or request body bugs.
        """
        # 1. Validate schema names before any work starts
        self._validate_schema_names()

        # 2. Parse metadata
        openapi_info = self._parse_openapi_info()
        django_metadata = self._parse_django_metadata()

        # 3. Parse schemas
        schemas = self._parse_all_schemas()

        # 4. Parse operations (may register inline schemas into self._inline_schemas)
        operations = self._parse_all_operations()

        # 5. Validate request bodies — hard stop on drf-spectacular schema bugs
        self._validate_request_bodies(operations)

        # 6. Merge inline schemas
        schemas.update(self._inline_schemas)

        return IRContext(
            openapi_info=openapi_info,
            django_metadata=django_metadata,
            schemas=schemas,
            operations=operations,
        )

    @abstractmethod
    def _detect_nullable(self, schema: SchemaObject) -> bool:
        """
        Detect if schema is nullable (version-specific).

        - OpenAPI30Parser: nullable: true
        - OpenAPIModernParser: type: ['string', 'null']
        """
        ...
