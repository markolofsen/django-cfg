"""
SchemaResolver - Unified transitive schema resolution for code generators.

Replaces the three diverging _get_schemas_for_operations implementations
in TypeScript, Python, and Go generators.
"""
from __future__ import annotations

from collections import deque
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..ir import IROperationObject, IRSchemaObject


class SchemaResolver:
    """
    Resolves all schemas transitively reachable from a set of operations.

    Handles $ref resolution through:
    - request_body and patch_request_body schema references
    - response schema references
    - nested property $refs
    - array items $refs
    - additional_properties $refs (previously missing in Go generator)
    """

    def __init__(self, all_schemas: dict[str, "IRSchemaObject"]):
        self._all = all_schemas

    def resolve_for_operations(
        self, operations: list["IROperationObject"]
    ) -> dict[str, "IRSchemaObject"]:
        """Return all schemas reachable from the given operations (transitively)."""
        seeds = self._collect_direct_schema_names(operations)
        return self._resolve_transitive(seeds)

    def _collect_direct_schema_names(
        self, operations: list["IROperationObject"]
    ) -> set[str]:
        """Collect schema names directly referenced by operations."""
        names: set[str] = set()
        for op in operations:
            if op.request_body and op.request_body.schema_name:
                names.add(op.request_body.schema_name)
            if op.patch_request_body and op.patch_request_body.schema_name:
                names.add(op.patch_request_body.schema_name)
            for response in op.responses.values():
                if response.schema_name:
                    names.add(response.schema_name)
                if response.items_schema_name:
                    names.add(response.items_schema_name)
        return names

    def _resolve_transitive(
        self, seeds: set[str]
    ) -> dict[str, "IRSchemaObject"]:
        """BFS expansion of $ref chains starting from seed schema names."""
        result: dict[str, "IRSchemaObject"] = {}
        queue: deque[str] = deque(
            name for name in seeds if name in self._all
        )
        while queue:
            name = queue.popleft()
            if name in result:
                continue
            schema = self._all[name]
            result[name] = schema
            for ref in self._collect_refs_from_schema(schema):
                if ref not in result and ref in self._all:
                    queue.append(ref)
        return result

    def _collect_refs_from_schema(self, schema: "IRSchemaObject") -> set[str]:
        """Collect all $ref names one level deep from a schema."""
        refs: set[str] = set()
        if schema.properties:
            for prop in schema.properties.values():
                if prop.ref:
                    refs.add(prop.ref)
                if prop.items and prop.items.ref:
                    refs.add(prop.items.ref)
                if prop.additional_properties and prop.additional_properties.ref:
                    refs.add(prop.additional_properties.ref)
        if schema.items and schema.items.ref:
            refs.add(schema.items.ref)
        if schema.additional_properties and schema.additional_properties.ref:
            refs.add(schema.additional_properties.ref)
        return refs
