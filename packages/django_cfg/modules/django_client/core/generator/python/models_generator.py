"""
Models Generator - Generates Pydantic models and enums.

Handles:
- Pydantic 2 model classes (Request/Response/Patch)
- Enum classes (StrEnum, IntEnum)
- Field validation and constraints
"""

from __future__ import annotations

from jinja2 import Environment

from ...ir import IRSchemaObject
from ..base import GeneratedFile


class ModelsGenerator:
    """Generates Pydantic models and enum classes."""

    def __init__(self, jinja_env: Environment, context, base_generator):
        """
        Initialize models generator.

        Args:
            jinja_env: Jinja2 environment for templates
            context: Generation context with schemas
            base_generator: Reference to base generator for utility methods
        """
        self.jinja_env = jinja_env
        self.context = context
        self.base = base_generator

    def generate_models_file(self) -> GeneratedFile:
        """Generate models.py with all Pydantic models."""
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

        template = self.jinja_env.get_template('models/models.py.jinja')
        content = template.render(
            has_enums=bool(self.base.get_enum_schemas()),
            schemas=schema_codes
        )

        return GeneratedFile(
            path="models.py",
            content=content,
            description="Pydantic 2 models (Request/Response/Patch)",
        )

    def generate_enums_file(self) -> GeneratedFile:
        """Generate enums.py with all Enum classes (flat structure)."""
        # Generate all enums
        enum_codes = []
        for name, schema in self.base.get_enum_schemas().items():
            enum_codes.append(self.generate_enum(schema))

        template = self.jinja_env.get_template('models/enums.py.jinja')
        content = template.render(enums=enum_codes)

        return GeneratedFile(
            path="enums.py",
            content=content,
            description="Enum classes from x-enum-varnames",
        )

    def generate_shared_enums_file(self, enums: dict[str, IRSchemaObject]) -> GeneratedFile:
        """Generate shared enums.py for namespaced structure (Variant 2)."""
        # Generate all enums
        enum_codes = []
        for name, schema in enums.items():
            enum_codes.append(self.generate_enum(schema))

        template = self.jinja_env.get_template('models/enums.py.jinja')
        content = template.render(enums=enum_codes)

        return GeneratedFile(
            path="enums.py",
            content=content,
            description="Shared enum classes from x-enum-varnames",
        )

    def generate_schema(self, schema: IRSchemaObject) -> str:
        """Generate Pydantic model for schema."""
        if schema.type != "object":
            # For primitive types, skip (they'll be inlined)
            return ""

        # Class docstring
        docstring_lines = []
        if schema.description:
            docstring_lines.extend(self.base.wrap_comment(schema.description, 76))

        # Add metadata about model type
        if schema.is_request_model:
            docstring_lines.append("")
            docstring_lines.append("Request model (no read-only fields).")
        elif schema.is_patch_model:
            docstring_lines.append("")
            docstring_lines.append("PATCH model (all fields optional).")
        elif schema.is_response_model:
            docstring_lines.append("")
            docstring_lines.append("Response model (includes read-only fields).")

        docstring = "\n".join(docstring_lines) if docstring_lines else None

        # Fields
        field_lines = []
        for prop_name, prop_schema in schema.properties.items():
            field_lines.append(self._generate_field(prop_name, prop_schema, schema.required))

        template = self.jinja_env.get_template('models/schema_class.py.jinja')
        return template.render(
            name=schema.name,
            docstring=docstring,
            fields=field_lines,
            is_response_model=schema.is_response_model,
        )

    def _generate_field(
        self,
        name: str,
        schema: IRSchemaObject,
        required_fields: list[str],
    ) -> str:
        """
        Generate Pydantic field definition.

        Examples:
            id: int
            username: str
            email: str | None = None
            age: int = Field(..., ge=0, le=150)
            status: StatusEnum
        """
        # Check if this field is an enum
        if schema.enum and schema.name:
            # Use enum type from shared enums (sanitized to PascalCase)
            python_type = self.base.sanitize_enum_name(schema.name)
            if schema.nullable:
                python_type = f"{python_type} | None"
        # Check if this field is a reference to an enum (via $ref)
        elif schema.ref and schema.ref in self.context.schemas:
            ref_schema = self.context.schemas[schema.ref]
            if ref_schema.enum:
                # This is a reference to an enum component (sanitized to PascalCase)
                python_type = self.base.sanitize_enum_name(schema.ref)
                if schema.nullable:
                    python_type = f"{python_type} | None"
            else:
                # Regular reference
                python_type = schema.python_type
        else:
            # Get Python type
            python_type = schema.python_type

        # Check if required
        is_required = name in required_fields

        # Build Field() kwargs
        field_kwargs = []

        if schema.description:
            field_kwargs.append(f"description={schema.description!r}")

        # Validation constraints
        if schema.min_length is not None:
            field_kwargs.append(f"min_length={schema.min_length}")
        if schema.max_length is not None:
            field_kwargs.append(f"max_length={schema.max_length}")
        if schema.pattern:
            field_kwargs.append(f"pattern={schema.pattern!r}")
        if schema.minimum is not None:
            # Convert to int for integer types to avoid float scientific notation
            min_val = int(schema.minimum) if schema.type == "integer" and isinstance(schema.minimum, float) else schema.minimum
            field_kwargs.append(f"ge={min_val}")
        if schema.maximum is not None:
            # Convert to int for integer types to avoid float scientific notation
            max_val = int(schema.maximum) if schema.type == "integer" and isinstance(schema.maximum, float) else schema.maximum
            field_kwargs.append(f"le={max_val}")

        # Example
        if schema.example:
            field_kwargs.append(f"examples=[{schema.example!r}]")

        # Default value
        if is_required:
            if field_kwargs:
                default = f"Field({', '.join(field_kwargs)})"
            else:
                default = "..."
        else:
            if field_kwargs:
                default = f"Field(None, {', '.join(field_kwargs)})"
            else:
                default = "None"

        return f"{name}: {python_type} = {default}"

    def generate_enum(self, schema: IRSchemaObject) -> str:
        """Generate Enum class from x-enum-varnames."""
        # Determine enum base class
        if schema.type == "integer":
            base_class = "IntEnum"
        else:
            base_class = "StrEnum"

        # Sanitize enum class name (convert to PascalCase)
        # "OrderDetail.status" → "OrderDetailStatus"
        # "Currency.currency_type" → "CurrencyCurrencyType"
        enum_name = self.base.sanitize_enum_name(schema.name)

        # Class docstring
        docstring = None
        if schema.description:
            # Format enum description to split bullet points
            docstring = self.base.format_enum_description(schema.description)

        # Enum members
        member_lines = []
        for var_name, value in zip(schema.enum_var_names, schema.enum):
            # Skip empty values (from blank=True in Django)
            if not var_name or (isinstance(value, str) and value == ''):
                continue

            if isinstance(value, str):
                member_lines.append(f'{var_name} = "{value}"')
            else:
                member_lines.append(f"{var_name} = {value}")

        template = self.jinja_env.get_template('models/enum_class.py.jinja')
        return template.render(
            name=enum_name,
            base_class=base_class,
            docstring=docstring,
            members=member_lines
        )

    def generate_app_models_file(
        self,
        tag: str,
        schemas: dict[str, IRSchemaObject],
        operations: list
    ) -> GeneratedFile:
        """Generate models.py for a specific app (namespaced structure)."""
        schema_codes = []

        # Collect enum names used in these schemas
        enum_names = set()

        # Track seen schema names to avoid duplicates
        seen_schemas = set()

        # Response models
        for name, schema in schemas.items():
            if schema.is_response_model and name not in seen_schemas:
                schema_codes.append(self.generate_schema(schema))
                seen_schemas.add(name)
                # Collect enums from properties
                if schema.properties:
                    for prop in schema.properties.values():
                        if prop.enum and prop.name:
                            enum_names.add(self.base.sanitize_enum_name(prop.name))
                        elif prop.ref and prop.ref in self.context.schemas:
                            ref_schema = self.context.schemas[prop.ref]
                            if ref_schema.enum:
                                enum_names.add(self.base.sanitize_enum_name(prop.ref))

        # Request models
        for name, schema in schemas.items():
            if schema.is_request_model and name not in seen_schemas:
                schema_codes.append(self.generate_schema(schema))
                seen_schemas.add(name)
                # Collect enums from properties
                if schema.properties:
                    for prop in schema.properties.values():
                        if prop.enum and prop.name:
                            enum_names.add(self.base.sanitize_enum_name(prop.name))
                        elif prop.ref and prop.ref in self.context.schemas:
                            ref_schema = self.context.schemas[prop.ref]
                            if ref_schema.enum:
                                enum_names.add(self.base.sanitize_enum_name(prop.ref))

        # Patch models
        for name, schema in schemas.items():
            if schema.is_patch_model and name not in seen_schemas:
                schema_codes.append(self.generate_schema(schema))
                seen_schemas.add(name)
                # Collect enums from properties
                if schema.properties:
                    for prop in schema.properties.values():
                        if prop.enum and prop.name:
                            enum_names.add(self.base.sanitize_enum_name(prop.name))
                        elif prop.ref and prop.ref in self.context.schemas:
                            ref_schema = self.context.schemas[prop.ref]
                            if ref_schema.enum:
                                enum_names.add(self.base.sanitize_enum_name(prop.ref))

        template = self.jinja_env.get_template('models/app_models.py.jinja')
        content = template.render(
            has_enums=len(enum_names) > 0,
            enum_names=sorted(enum_names),  # Sort for consistent output
            schemas=schema_codes
        )

        folder_name = self.base.tag_and_app_to_folder_name(tag, operations)
        return GeneratedFile(
            path=f"{folder_name}/models.py",
            content=content,
            description=f"Models for {tag}",
        )
