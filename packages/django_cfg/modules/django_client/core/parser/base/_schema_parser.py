"""
Schema parsing mixin — converts OpenAPI SchemaObjects to IRSchemaObjects.
"""

from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models import ReferenceObject, SchemaObject
    from ...ir import IRSchemaObject


class SchemaParserMixin:
    """Parses OpenAPI component schemas and inline schemas to IRSchemaObject."""

    def _parse_all_schemas(self) -> dict[str, IRSchemaObject]:
        """
        Parse all schemas from components.

        Note: Schema name validation is done in _validate_schema_names()
        which is called BEFORE this method in parse().
        """
        if not self.spec.components or not self.spec.components.schemas:
            return {}

        from ..models import ReferenceObject
        schemas = {}
        for name, schema_or_ref in self.spec.components.schemas.items():
            if isinstance(schema_or_ref, ReferenceObject):
                continue
            schemas[name] = self._parse_schema(name, schema_or_ref)
        return schemas

    def _parse_schema(self, name: str, schema: SchemaObject) -> IRSchemaObject:
        """Parse SchemaObject to IRSchemaObject."""
        if name in self._schema_cache:
            return self._schema_cache[name]

        from ..models import ReferenceObject
        from ...ir import IRSchemaObject

        is_request = name.endswith("Request")
        is_patch = name.startswith("Patched")
        is_response = not is_request and not is_patch

        related_request = None
        related_response = None

        if is_response:
            potential_request = f"{name}Request"
            if self._schema_exists(potential_request):
                related_request = potential_request

        if is_request:
            base_name = name[:-7]
            if self._schema_exists(base_name):
                related_response = base_name

        if is_patch:
            base_name = name[7:]
            if self._schema_exists(base_name):
                related_response = base_name

        properties = {}
        if schema.properties:
            for prop_name, prop_schema_or_ref in schema.properties.items():
                if isinstance(prop_schema_or_ref, ReferenceObject):
                    properties[prop_name] = self._resolve_ref(prop_schema_or_ref)
                else:
                    ref_from_combinator = self._extract_ref_from_combinators(prop_schema_or_ref)
                    if ref_from_combinator:
                        resolved_schema = self._resolve_ref(ref_from_combinator)
                        if self._detect_nullable(prop_schema_or_ref):
                            resolved_schema.nullable = True
                        properties[prop_name] = resolved_schema
                    else:
                        properties[prop_name] = self._parse_schema(
                            f"{name}.{prop_name}", prop_schema_or_ref
                        )

        items = None
        if schema.items:
            if isinstance(schema.items, ReferenceObject):
                items = self._resolve_ref(schema.items)
            else:
                items = self._parse_schema(f"{name}.items", schema.items)

        additional_properties = None
        if schema.additionalProperties and not isinstance(schema.additionalProperties, bool):
            if isinstance(schema.additionalProperties, ReferenceObject):
                additional_properties = self._resolve_ref(schema.additionalProperties)
            else:
                additional_properties = self._parse_schema(
                    f"{name}.additionalProperties", schema.additionalProperties
                )
        elif schema.additionalProperties is True:
            additional_properties = IRSchemaObject(name=f"{name}.additionalProperties", type="any")

        normalized_type = self._normalize_type(schema)
        if (normalized_type == "object" and
                not properties and
                not additional_properties and
                schema.additionalProperties is not False):
            additional_properties = IRSchemaObject(name=f"{name}.additionalProperties", type="any")

        name_to_use = name
        if schema.x_spec_enum_id and schema.enum:
            if schema.x_spec_enum_id in self._enum_id_to_name:
                name_to_use = self._enum_id_to_name[schema.x_spec_enum_id]
            else:
                self._enum_id_to_name[schema.x_spec_enum_id] = name

        ir_schema = IRSchemaObject(
            name=name_to_use,
            type=normalized_type,
            format=schema.format,
            description=schema.description,
            nullable=self._detect_nullable(schema),
            properties=properties,
            required=schema.required or [],
            additional_properties=additional_properties,
            items=items,
            enum=[v for v in schema.enum if v is not None] if schema.enum else None,
            enum_var_names=schema.x_enum_varnames,
            enum_id=schema.x_spec_enum_id,
            const=schema.const,
            is_request_model=is_request,
            is_response_model=is_response,
            is_patch_model=is_patch,
            related_request=related_request,
            related_response=related_response,
            min_length=schema.minLength,
            max_length=schema.maxLength,
            pattern=schema.pattern,
            minimum=schema.minimum,
            maximum=schema.maximum,
            read_only=schema.readOnly,
            write_only=schema.writeOnly,
            deprecated=schema.deprecated,
            default=schema.default,
        )

        self._schema_cache[name] = ir_schema
        return ir_schema

    def _schema_exists(self, name: str) -> bool:
        """Check if schema exists in components."""
        if not self.spec.components or not self.spec.components.schemas:
            return False
        return name in self.spec.components.schemas

    def _resolve_ref(self, ref: ReferenceObject) -> IRSchemaObject:
        """Resolve $ref to a lightweight IRSchemaObject reference stub."""
        from ...ir import IRSchemaObject
        if not ref.ref.startswith("#/components/schemas/"):
            raise ValueError(f"Unsupported $ref format: {ref.ref}")
        schema_name = ref.ref.split("/")[-1]
        return IRSchemaObject(name=schema_name, type="object", ref=schema_name)

    def _extract_ref_from_combinators(self, schema: SchemaObject) -> ReferenceObject | None:
        """
        Extract $ref from allOf/anyOf/oneOf if present.

        DRF-spectacular wraps enum refs in allOf:
            "status": {"allOf": [{"$ref": "..."}], "description": "..."}
        """
        from ..models import ReferenceObject
        for combinator in (schema.allOf, schema.anyOf, schema.oneOf):
            if combinator:
                for item in combinator:
                    if isinstance(item, ReferenceObject):
                        return item
        return None

    @abstractmethod
    def _detect_nullable(self, schema: SchemaObject) -> bool:
        """Version-specific nullable detection. Implemented by OpenAPI30/Modern parsers."""
        ...

    def _normalize_type(self, schema: SchemaObject) -> str:
        """Normalize schema type to a single string (handles OAS 3.1 type arrays)."""
        from ..models import SchemaObject as _Schema
        if schema.base_type:
            return schema.base_type

        if schema.anyOf and len(schema.anyOf) == 2:
            for item in schema.anyOf:
                if isinstance(item, _Schema) and item.base_type and item.base_type != 'null':
                    return item.base_type

        if schema.oneOf and len(schema.oneOf) == 2:
            has_null = False
            has_empty = False
            actual_type = None
            for item in schema.oneOf:
                if isinstance(item, _Schema):
                    if item.base_type == 'null':
                        has_null = True
                    elif item.base_type:
                        actual_type = item.base_type
                    else:
                        has_empty = True
            if has_null and has_empty:
                return "any"
            if has_null and actual_type:
                return actual_type

        if schema.properties is not None:
            return "object"
        if schema.items is not None:
            return "array"

        if (not schema.base_type and
                not schema.properties and
                not schema.items and
                not schema.anyOf and
                not schema.oneOf and
                not schema.allOf):
            return "object"

        if schema.description:
            desc_lower = schema.description.lower()
            if any(kw in desc_lower for kw in ['json', 'configuration', 'settings', 'config', 'dict']):
                return "object"

        return "string"

    def _schema_has_binary_field(self, schema_name: str) -> bool:
        """Check if a schema has any binary (file upload) fields."""
        from ..models import ReferenceObject
        if not self.spec.components or not self.spec.components.schemas:
            return False
        schema = self.spec.components.schemas.get(schema_name)
        if not schema or isinstance(schema, ReferenceObject):
            return False
        if not schema.properties:
            return False
        for prop_schema in schema.properties.values():
            if isinstance(prop_schema, ReferenceObject):
                continue
            if prop_schema.format == "binary":
                return True
        return False

    def _to_pascal_case(self, name: str) -> str:
        from ...utils.naming import to_pascal_case
        return to_pascal_case(name)
