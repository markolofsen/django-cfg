"""
Zod Schemas Generator - Generates Zod validation schemas from IR.

This generator creates Zod schemas for runtime validation:
- Object schemas (z.object)
- Enum schemas (z.nativeEnum)
- Array schemas (z.array)
- Type inference (z.infer<typeof Schema>)
"""

from __future__ import annotations

from jinja2 import Environment
from ..base import GeneratedFile, BaseGenerator
from ...ir import IRContext, IRSchemaObject


class SchemasGenerator:
    """
    Generate Zod schemas from IR schemas.

    Features:
    - Runtime validation with Zod
    - Type inference from schemas
    - Enum validation with z.nativeEnum()
    - Nested object validation
    - Array and nullable types
    """

    def __init__(self, jinja_env: Environment, context: IRContext, base: BaseGenerator):
        self.jinja_env = jinja_env
        self.context = context
        self.base = base

    def generate_schema(self, schema: IRSchemaObject) -> str:
        """
        Generate Zod schema for a single IR schema.

        Args:
            schema: IRSchemaObject to convert to Zod

        Returns:
            Zod schema code as string

        Examples:
            >>> generate_schema(User)
            export const UserSchema = z.object({
              id: z.number(),
              email: z.string().email(),
              username: z.string().min(1).max(150),
            })
        """
        if schema.type == "object":
            return self._generate_object_schema(schema)
        elif schema.type == "array":
            return self._generate_array_schema(schema)
        elif schema.enum:
            return self._generate_enum_schema(schema)
        else:
            # Primitive type
            return self._map_type_to_zod(schema)

    def _generate_object_schema(self, schema: IRSchemaObject) -> str:
        """Generate z.object() schema."""
        lines = []

        # Schema comment
        if schema.description:
            lines.append(f"/**\n * {schema.description}\n */")

        # Start schema definition
        lines.append(f"export const {schema.name}Schema = z.object({{")

        # Generate fields
        if schema.properties:
            for prop_name, prop_schema in schema.properties.items():
                field_code = self._generate_field(prop_name, prop_schema, schema.required)
                lines.append(f"  {field_code},")

        lines.append("})")

        return "\n".join(lines)

    def _generate_field(
        self,
        name: str,
        schema: IRSchemaObject,
        required_fields: list[str],
    ) -> str:
        """
        Generate Zod field validation.

        Examples:
            id: z.number()
            email: z.string().email()
            username: z.string().min(1).max(150)
            status: z.nativeEnum(Enums.StatusEnum)
            created_at: z.string().datetime()
        """
        # Check if this field is an enum
        if schema.enum and schema.name:
            # Use enum validation
            zod_type = f"z.nativeEnum(Enums.{self.base.sanitize_enum_name(schema.name)})"
        # Check if this field is a reference to an enum
        elif schema.ref and schema.ref in self.context.schemas:
            ref_schema = self.context.schemas[schema.ref]
            if ref_schema.enum:
                # Reference to enum component
                zod_type = f"z.nativeEnum(Enums.{self.base.sanitize_enum_name(schema.ref)})"
            else:
                # Reference to another schema
                zod_type = f"{schema.ref}Schema"
        else:
            # Map TypeScript type to Zod type
            zod_type = self._map_type_to_zod(schema)

        # Check if required
        is_required = name in required_fields

        # Handle optional fields - use .optional() for both non-required AND nullable
        # This converts Django's nullable=True to TypeScript's optional (undefined)
        if not is_required or schema.nullable:
            zod_type = f"{zod_type}.optional()"

        return f"{name}: {zod_type}"

    def _map_type_to_zod(self, schema: IRSchemaObject) -> str:
        """
        Map OpenAPI/TypeScript type to Zod validation.

        Args:
            schema: IRSchemaObject with type information

        Returns:
            Zod validation code

        Examples:
            string -> z.string()
            string (format: email) -> z.string().email()
            string (format: date-time) -> z.string().datetime()
            string (format: uri) -> z.string().url()
            integer -> z.number().int()
            number -> z.number()
            boolean -> z.boolean()
            array -> z.array(...)
        """
        schema_type = schema.type
        schema_format = schema.format

        # String types with format validation
        if schema_type == "string":
            base_type = "z.string()"

            # Add format validation
            if schema_format == "email":
                base_type = "z.string().email()"
            elif schema_format in ("date-time", "datetime"):
                base_type = "z.string().datetime()"
            elif schema_format == "date":
                base_type = "z.string().date()"
            elif schema_format in ("uri", "url"):
                base_type = "z.string().url()"
            elif schema_format == "uuid":
                base_type = "z.string().uuid()"

            # Add length constraints
            if schema.min_length is not None:
                base_type = f"{base_type}.min({schema.min_length})"
            if schema.max_length is not None:
                base_type = f"{base_type}.max({schema.max_length})"

            # Add pattern validation
            if schema.pattern:
                # Escape regex pattern for JS
                escaped_pattern = schema.pattern.replace('\\', '\\\\')
                base_type = f"{base_type}.regex(/{escaped_pattern}/)"

            return base_type

        # Integer type
        elif schema_type == "integer":
            base_type = "z.number().int()"

            # Add range constraints
            if schema.minimum is not None:
                base_type = f"{base_type}.min({schema.minimum})"
            if schema.maximum is not None:
                base_type = f"{base_type}.max({schema.maximum})"

            return base_type

        # Number type
        elif schema_type == "number":
            base_type = "z.number()"

            # Add range constraints
            if schema.minimum is not None:
                base_type = f"{base_type}.min({schema.minimum})"
            if schema.maximum is not None:
                base_type = f"{base_type}.max({schema.maximum})"

            return base_type

        # Boolean type
        elif schema_type == "boolean":
            return "z.boolean()"

        # Array type
        elif schema_type == "array":
            if schema.items:
                item_type = self._map_type_to_zod(schema.items)
                return f"z.array({item_type})"
            return "z.array(z.any())"

        # Object type
        elif schema_type == "object":
            # Only reference schema if it's a defined component (not an inline property)
            # Inline objects should use z.record() or z.object({})
            if schema.ref:
                # Explicit reference
                return f"{schema.ref}Schema"
            elif schema.properties:
                # Inline object with properties - shouldn't reach here, but use z.object
                return "z.object({})"
            else:
                # Object with no properties (like additionalProperties: {})
                # Use z.record(z.string(), z.any()) for dynamic objects
                return "z.record(z.string(), z.any())"

        # Fallback to any
        return "z.any()"

    def _generate_array_schema(self, schema: IRSchemaObject) -> str:
        """Generate z.array() schema."""
        lines = []

        if schema.description:
            lines.append(f"/**\n * {schema.description}\n */")

        item_type = "z.any()"
        if schema.items:
            item_type = self._map_type_to_zod(schema.items)

        lines.append(f"export const {schema.name}Schema = z.array({item_type})")

        return "\n".join(lines)

    def _generate_enum_schema(self, schema: IRSchemaObject) -> str:
        """Generate z.nativeEnum() schema."""
        enum_name = self.base.sanitize_enum_name(schema.name)

        lines = []

        if schema.description:
            lines.append(f"/**\n * {schema.description}\n */")

        lines.append(f"export const {enum_name}Schema = z.nativeEnum(Enums.{enum_name})")

        return "\n".join(lines)

    def generate_schema_file(self, schema: IRSchemaObject, refs: set[str]) -> GeneratedFile:
        """
        Generate individual Zod schema file.

        Args:
            schema: Schema to generate
            refs: Set of schema names that are referenced

        Returns:
            GeneratedFile with Zod schema
        """
        # Generate schema code
        schema_code = self.generate_schema(schema)

        # Check if has enums
        has_enums = self._schema_uses_enums(schema)

        # Render template
        template = self.jinja_env.get_template("schemas/schema.ts.jinja")
        content = template.render(
            schema_name=schema.name,
            description=schema.description,
            schema_code=schema_code,
            has_enums=has_enums,
            has_refs=bool(refs),
            refs=sorted(refs),
        )

        return GeneratedFile(
            path=f"_utils/schemas/{schema.name}.schema.ts",
            content=content,
            description=f"Zod schema for {schema.name}",
        )

    def generate_schemas_index_file(self, schema_names: list[str]) -> GeneratedFile:
        """Generate index.ts for schemas folder."""
        template = self.jinja_env.get_template("schemas/index.ts.jinja")
        content = template.render(schema_names=sorted(schema_names))

        return GeneratedFile(
            path="_utils/schemas/index.ts",
            content=content,
            description="Zod schemas index",
        )

    def _schema_uses_enums(self, schema: IRSchemaObject) -> bool:
        """Check if schema uses any enums."""
        if schema.enum:
            return True

        if schema.properties:
            for prop in schema.properties.values():
                if prop.enum or (prop.ref and self._is_enum_ref(prop.ref)):
                    return True

        if schema.items:
            if schema.items.enum or (schema.items.ref and self._is_enum_ref(schema.items.ref)):
                return True

        return False

    def _is_enum_ref(self, ref: str) -> bool:
        """Check if reference points to an enum."""
        if ref in self.context.schemas:
            return self.context.schemas[ref].enum is not None
        return False
