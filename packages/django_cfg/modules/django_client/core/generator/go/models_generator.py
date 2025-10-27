"""
Models Generator - Generates Go structs from IR schemas.

Handles generation of:
- Response models (User, Post, etc.)
- Request models (UserRequest, PostRequest)
- Patch models (PatchedUser, PatchedPost)
- Enum types with constants
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from jinja2 import Environment

    from ...ir import IRContext, IRSchemaObject
    from ..base import GeneratedFile
    from .generator import GoGenerator


class ModelsGenerator:
    """Generates Go struct definitions from IR schemas."""

    def __init__(
        self,
        jinja_env: Environment,
        context: IRContext,
        generator: GoGenerator,
    ):
        """
        Initialize models generator.

        Args:
            jinja_env: Jinja2 environment
            context: IRContext from parser
            generator: Parent GoGenerator instance
        """
        self.jinja_env = jinja_env
        self.context = context
        self.generator = generator

    def generate_models_file(self) -> GeneratedFile:
        """
        Generate models.go with all struct definitions.

        Contains:
        - All response models (User, Post, etc.)
        - All request models (UserRequest, PostRequest)
        - All patch models (PatchedUser, PatchedPost)

        Returns:
            GeneratedFile with models.go content
        """
        template = self.jinja_env.get_template("models.go.j2")

        structs = []

        # Generate response models
        for schema_name, schema in sorted(self.context.response_models.items()):
            struct_def = self.generator.type_mapper.ir_schema_to_struct(schema)
            structs.append(struct_def)

        # Generate request models
        for schema_name, schema in sorted(self.context.request_models.items()):
            struct_def = self.generator.type_mapper.ir_schema_to_struct(schema)
            structs.append(struct_def)

        # Generate patch models
        for schema_name, schema in sorted(self.context.patch_models.items()):
            struct_def = self.generator.type_mapper.ir_schema_to_struct(schema)
            structs.append(struct_def)

        # Collect imports
        imports = self._collect_imports(structs)

        content = template.render(
            package_name=self.generator.package_name,
            structs=structs,
            imports=imports,
            generated_at=datetime.now().isoformat(),
        )

        return self.generator._create_generated_file(
            path="models.go",
            content=content,
            description="API data models"
        )

    def generate_enums_file(self) -> GeneratedFile:
        """
        Generate enums.go with enum type definitions.

        Go approach to enums:
        ```go
        type StatusEnum int64

        const (
            StatusNew StatusEnum = 1
            StatusInProgress StatusEnum = 2
            StatusComplete StatusEnum = 3
        )

        func (s StatusEnum) String() string {
            switch s {
            case StatusNew:
                return "STATUS_NEW"
            case StatusInProgress:
                return "STATUS_IN_PROGRESS"
            case StatusComplete:
                return "STATUS_COMPLETE"
            default:
                return fmt.Sprintf("StatusEnum(%d)", s)
            }
        }

        func (s StatusEnum) MarshalJSON() ([]byte, error) {
            return json.Marshal(int64(s))
        }

        func (s *StatusEnum) UnmarshalJSON(data []byte) error {
            var v int64
            if err := json.Unmarshal(data, &v); err != nil {
                return err
            }
            *s = StatusEnum(v)
            return nil
        }
        ```

        Returns:
            GeneratedFile with enums.go content
        """
        template = self.jinja_env.get_template("enums.go.j2")

        enums = []
        for schema_name, schema in sorted(self.context.enum_schemas.items()):
            enum_def = self.generator.type_mapper.generate_enum_definition(schema)
            enums.append(enum_def)

        if not enums:
            # No enums to generate
            return None

        content = template.render(
            package_name=self.generator.package_name,
            enums=enums,
            generated_at=datetime.now().isoformat(),
        )

        return self.generator._create_generated_file(
            path="enums.go",
            content=content,
            description="API enum types"
        )

    def generate_shared_enums_file(self, enums: dict[str, IRSchemaObject]) -> GeneratedFile:
        """
        Generate shared enums.go (for namespaced structure).

        Args:
            enums: Dictionary of enum schemas

        Returns:
            GeneratedFile with shared enums.go content
        """
        template = self.jinja_env.get_template("enums.go.j2")

        enum_defs = []
        for schema_name, schema in sorted(enums.items()):
            enum_def = self.generator.type_mapper.generate_enum_definition(schema)
            enum_defs.append(enum_def)

        if not enum_defs:
            return None

        content = template.render(
            package_name="types",
            enums=enum_defs,
            generated_at=datetime.now().isoformat(),
        )

        return self.generator._create_generated_file(
            path="types/enums.go",
            content=content,
            description="Shared API enum types"
        )

    def generate_app_models_file(
        self,
        tag: str,
        schemas: dict[str, IRSchemaObject],
        operations: list,
    ) -> GeneratedFile:
        """
        Generate models.go for specific app/tag (namespaced structure).

        Args:
            tag: Tag name
            schemas: Schemas used by this app
            operations: Operations for this app

        Returns:
            GeneratedFile with app-specific models.go
        """
        template = self.jinja_env.get_template("models.go.j2")

        structs = []
        for schema_name, schema in sorted(schemas.items()):
            # Skip enum schemas (they go in shared enums.go)
            if schema.enum:
                continue

            struct_def = self.generator.type_mapper.ir_schema_to_struct(schema)
            structs.append(struct_def)

        if not structs:
            # No models for this app
            return None

        # Collect imports
        imports = self._collect_imports(structs)

        # Get folder name for this app
        folder_name = self.generator.tag_and_app_to_folder_name(tag, operations)

        content = template.render(
            package_name=folder_name,
            structs=structs,
            imports=imports,
            generated_at=datetime.now().isoformat(),
        )

        return self.generator._create_generated_file(
            path=f"{folder_name}/models.go",
            content=content,
            description=f"{tag} API models"
        )

    def _collect_imports(self, structs: list[dict]) -> list[str]:
        """
        Collect required imports for structs.

        Args:
            structs: List of struct definitions

        Returns:
            List of import paths

        Examples:
            >>> structs = [{"needs_time_import": True}]
            >>> imports = generator._collect_imports(structs)
            >>> "time" in imports
            True
        """
        imports = set()

        # Check if time import is needed
        for struct in structs:
            if struct.get("needs_time_import"):
                imports.add("time")

            # Check if types package is used (for enums)
            for field in struct.get("fields", []):
                if "types." in field.get("type", ""):
                    module_name = self.generator.package_config.get("module_name", "apiclient")
                    imports.add(f"{module_name}/types")
                    break

        return sorted(imports)

    def generate_schema(self, schema: IRSchemaObject) -> str:
        """
        Generate Go struct code for a single schema (for backward compatibility).

        Args:
            schema: IRSchemaObject to generate

        Returns:
            Generated struct code as string
        """
        struct_def = self.generator.type_mapper.ir_schema_to_struct(schema)

        lines = []

        # Add doc comment
        if struct_def["doc"]:
            lines.append(f"// {struct_def['doc']}")

        # Add struct definition
        lines.append(f"type {struct_def['name']} struct {{")

        # Add fields
        for field in struct_def["fields"]:
            if field["description"]:
                lines.append(f"\t// {field['description']}")

            lines.append(f"\t{field['name']} {field['type']} {field['json_tag']}")

        lines.append("}")

        return "\n".join(lines)
