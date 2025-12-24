"""
TypeScript Models Generator - Generates TypeScript interfaces and enums.
"""

from __future__ import annotations

from jinja2 import Environment

from ...ir import IRSchemaObject
from ..base import GeneratedFile


class ModelsGenerator:
    """Generates TypeScript interfaces and enums."""

    def __init__(self, jinja_env: Environment, context, base):
        self.jinja_env = jinja_env
        self.context = context
        self.base = base

    def generate_models_file(self):
        """Generate models.ts with all TypeScript interfaces."""

        # Generate all schemas
        schema_codes = []

        # Response models first
        for name, schema in self.base.get_response_schemas().items():
            schema_codes.append(self.generate_schema(schema))

        # Request models
        for name, schema in self.base.get_request_schemas().items():
            schema_codes.append(self.generate_schema(schema))

        # Patch models
        for name, schema in self.base.get_patch_schemas().items():
            schema_codes.append(self.generate_schema(schema))

        template = self.jinja_env.get_template('models/models.ts.jinja')
        content = template.render(
            has_enums=bool(self.base.get_enum_schemas()),
            schemas=schema_codes
        )

        return GeneratedFile(
            path="models.ts",
            content=content,
            description="TypeScript interfaces (Request/Response/Patch)",
        )

    def generate_enums_file(self):
        """Generate enums.ts with all enum types (flat structure)."""

        enum_codes = []
        for name, schema in self.base.get_enum_schemas().items():
            enum_codes.append(self.generate_enum(schema))

        template = self.jinja_env.get_template('models/enums.ts.jinja')
        content = template.render(enums=enum_codes)

        return GeneratedFile(
            path="enums.ts",
            content=content,
            description="Enum types from x-enum-varnames",
        )

    def generate_shared_enums_file(self, enums: dict[str, IRSchemaObject]):
        """Generate shared enums.ts for namespaced structure (Variant 2)."""

        enum_codes = []
        for name, schema in enums.items():
            enum_codes.append(self.generate_enum(schema))

        template = self.jinja_env.get_template('models/enums.ts.jinja')
        content = template.render(enums=enum_codes)

        return GeneratedFile(
            path="enums.ts",
            content=content,
            description="Shared enum types from x-enum-varnames",
        )

    def generate_schema(self, schema: IRSchemaObject) -> str:
        """Generate TypeScript interface for schema."""
        # Handle binary types as type aliases (for file uploads)
        if schema.is_binary:
            comment = f"/**\n * {schema.description}\n */" if schema.description else None
            lines = []
            if comment:
                lines.append(comment)
            lines.append(f"export type {schema.name} = File | Blob;")
            return "\n".join(lines)

        if schema.type != "object":
            # For primitive types, skip (they'll be inlined)
            return ""

        # Interface comment
        comment_lines = []
        if schema.description:
            comment_lines.extend(self.base.wrap_comment(schema.description, 76))

        # Add metadata about model type
        if schema.is_request_model:
            comment_lines.append("")
            comment_lines.append("Request model (no read-only fields).")
        elif schema.is_patch_model:
            comment_lines.append("")
            comment_lines.append("PATCH model (all fields optional).")
        elif schema.is_response_model:
            comment_lines.append("")
            comment_lines.append("Response model (includes read-only fields).")

        comment = "/**\n * " + "\n * ".join(comment_lines) + "\n */" if comment_lines else None

        # Fields
        field_lines = []

        for prop_name, prop_schema in schema.properties.items():
            field_lines.append(self._generate_field(prop_name, prop_schema, schema.required))

        # Build interface
        lines = []

        if comment:
            lines.append(comment)

        lines.append(f"export interface {schema.name} {{")

        if field_lines:
            for field_line in field_lines:
                lines.append(self.base.indent(field_line, 2))
        else:
            # Empty interface
            pass

        lines.append("}")

        return "\n".join(lines)

    def _generate_field(
        self,
        name: str,
        schema: IRSchemaObject,
        required_fields: list[str],
    ) -> str:
        """
        Generate TypeScript field definition.

        Examples:
            id: number;
            username: string;
            email?: string;
            status: Enums.StatusEnum;
        """
        # Check if this field is an enum
        if schema.enum and schema.name:
            # Use enum type from shared enums (sanitized)
            ts_type = f"Enums.{self.base.sanitize_enum_name(schema.name)}"
            # Don't add | null for nullable - use optional marker instead
        # Check if this field is a reference to an enum (via $ref)
        elif schema.ref and schema.ref in self.context.schemas:
            ref_schema = self.context.schemas[schema.ref]
            if ref_schema.enum:
                # This is a reference to an enum component (sanitized to PascalCase)
                ts_type = f"Enums.{self.base.sanitize_enum_name(schema.ref)}"
                # Don't add | null for nullable - use optional marker instead
            else:
                # Regular reference - get base type without | null
                ts_type = schema.typescript_type
                # Remove | null suffix if present (we'll use optional marker instead)
                if ts_type.endswith(" | null"):
                    ts_type = ts_type[:-7]  # Remove " | null"
        else:
            # Get TypeScript type
            ts_type = schema.typescript_type
            # Remove | null suffix to rebuild it properly based on schema.nullable
            if ts_type.endswith(" | null"):
                ts_type = ts_type[:-7]  # Remove " | null"

        # Check if required
        is_required = name in required_fields

        # Handle nullable and optional separately
        # - nullable: add | null to type
        # - not required: add ? optional marker
        # Special case: readOnly + nullable fields should be optional
        # (they're always in response but can be null, so from client perspective they're optional)
        if schema.nullable:
            ts_type = f"{ts_type} | null"
            # Make readOnly nullable fields optional
            if schema.read_only:
                is_required = False

        optional_marker = "" if is_required else "?"

        # Comment
        if schema.description:
            return f"/** {schema.description} */\n{name}{optional_marker}: {ts_type};"

        return f"{name}{optional_marker}: {ts_type};"

    def generate_enum(self, schema: IRSchemaObject) -> str:
        """Generate TypeScript enum from x-enum-varnames."""
        # Sanitize enum name (convert to PascalCase)
        # "OrderDetail.status" → "OrderDetailStatus"
        # "Currency.currency_type" → "CurrencyCurrencyType"
        enum_name = self.base.sanitize_enum_name(schema.name)

        # Enum comment
        comment = None
        if schema.description:
            # Format enum description to split bullet points
            formatted_desc = self.base.format_enum_description(schema.description)
            # Split into lines and format as JSDoc comment
            desc_lines = formatted_desc.split('\n')
            comment = "/**\n * " + "\n * ".join(desc_lines) + "\n */"

        # Enum members
        member_lines = []
        for var_name, value in zip(schema.enum_var_names, schema.enum):
            # Skip empty values (from blank=True in Django)
            if not var_name or (isinstance(value, str) and value == ''):
                continue

            # Sanitize var_name: replace special chars with words/underscores, convert to UPPER_CASE
            # "A+" -> "A_PLUS", "A-" -> "A_MINUS", "TAR.GZ" -> "TAR_DOT_GZ", "TAR GZ" -> "TAR_GZ"
            # "urn:ietf:params:oauth:grant-type:device_code" -> "URN_IETF_PARAMS_OAUTH_GRANT_TYPE_DEVICE_CODE"
            sanitized_var_name = (var_name
                .replace('+', '_PLUS')
                .replace('-', '_MINUS')
                .replace('.', '_DOT_')
                .replace(':', '_')  # Handle URN/URI format (e.g., urn:ietf:params:oauth:grant-type:device_code)
                .replace(' ', '_')
                .upper())

            if isinstance(value, str):
                member_lines.append(f'{sanitized_var_name} = "{value}",')
            else:
                member_lines.append(f"{sanitized_var_name} = {value},")

        # Build enum
        lines = []

        if comment:
            lines.append(comment)

        lines.append(f"export enum {enum_name} {{")

        for member_line in member_lines:
            lines.append(self.base.indent(member_line, 2))

        lines.append("}")

        return "\n".join(lines)

    def generate_app_models_file(self, tag: str, schemas: dict[str, IRSchemaObject], operations: list):
        """Generate models.ts for a specific app."""

        # Check if we have enums in schemas
        app_enums = self.base._collect_enums_from_schemas(schemas)
        has_enums = len(app_enums) > 0

        # Generate schemas
        schema_codes = []
        for name, schema in schemas.items():
            schema_codes.append(self.generate_schema(schema))

        template = self.jinja_env.get_template('models/app_models.ts.jinja')
        content = template.render(
            has_enums=has_enums,
            schemas=schema_codes
        )

        folder_name = self.base.tag_and_app_to_folder_name(tag, operations)
        return GeneratedFile(
            path=f"{folder_name}/models.ts",
            content=content,
            description=f"TypeScript interfaces for {tag}",
        )
