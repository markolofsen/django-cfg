"""
ParserState Protocol — structural type for mixin self-access.

All mixins access shared parser state via this Protocol,
which BaseParser satisfies through its __init__ assignments.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable, TYPE_CHECKING

if TYPE_CHECKING:
    from ..models import OpenAPISpec, ReferenceObject, SchemaObject
    from ...ir import IRSchemaObject


@runtime_checkable
class ParserState(Protocol):
    spec: OpenAPISpec
    _schema_cache: dict[str, IRSchemaObject]
    _inline_schemas: dict[str, IRSchemaObject]
    _enum_id_to_name: dict[str, str]

    # Core methods used across mixins — declared here so Pyright
    # resolves cross-mixin calls without type: ignore comments.
    def _schema_exists(self, name: str) -> bool: ...
    def _resolve_ref(self, ref: ReferenceObject) -> IRSchemaObject: ...
    def _parse_schema(self, name: str, schema: SchemaObject) -> IRSchemaObject: ...
    def _normalize_type(self, schema: SchemaObject) -> str: ...
    def _detect_nullable(self, schema: SchemaObject) -> bool: ...
    def _schema_has_binary_field(self, schema_name: str) -> bool: ...
