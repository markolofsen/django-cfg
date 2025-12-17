"""
Go Generator - Main orchestrator for Go client generation.

Coordinates all sub-generators:
- ModelsGenerator: Go structs and enums
- OperationsGenerator: Operation methods
- ClientGenerator: HTTP client
- FilesGenerator: Auxiliary files (go.mod, README, Makefile)
"""

from __future__ import annotations

import pathlib

from jinja2 import Environment, FileSystemLoader, select_autoescape

from ...ir import IROperationObject, IRSchemaObject
from ..base import BaseGenerator, GeneratedFile
from ..claude_generator import ClaudeGenerator
from .client_generator import ClientGenerator
from .files_generator import FilesGenerator
from .models_generator import ModelsGenerator
from .naming import get_go_package_name
from .operations_generator import OperationsGenerator
from .type_mapper import GoTypeMapper


class GoGenerator(BaseGenerator):
    """
    Go client generator.

    Generates:
    - models.go: Go structs (User, UserRequest, PatchedUser)
    - enums.go: Enum types with constants
    - client.go: HTTP client with all operations
    - errors.go: API error handling
    - go.mod: Module definition
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Setup Jinja2 environment
        templates_dir = pathlib.Path(__file__).parent / "templates"
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Initialize type mapper
        # Use types package for namespaced structure to avoid import cycles
        use_types_pkg = self.client_structure == "namespaced"
        self.type_mapper = GoTypeMapper(use_types_package=use_types_pkg)

        # Get package name
        self.package_name = get_go_package_name(
            self.package_config.get("name", "apiclient")
        )

        # Initialize sub-generators
        self.models_gen = ModelsGenerator(self.jinja_env, self.context, self)
        self.operations_gen = OperationsGenerator(self.jinja_env, self.context, self)
        self.client_gen = ClientGenerator(self.jinja_env, self.context, self, self.operations_gen)
        self.files_gen = FilesGenerator(self.jinja_env, self.context, self)

    def generate(self) -> list[GeneratedFile]:
        """Generate all Go client files."""
        files = []

        if self.client_structure == "namespaced":
            # Generate per-app folders
            ops_by_tag = self.group_operations_by_tag()

            for tag, operations in sorted(ops_by_tag.items()):
                # Generate app folder (models.go, operations.go)
                app_files = self._generate_app_folder(tag, operations)
                if app_files:
                    files.extend(app_files)

            # Generate shared enums.go
            all_schemas = self.context.schemas
            all_enums = self._collect_enums_from_schemas(all_schemas)
            if all_enums:
                enum_file = self.models_gen.generate_shared_enums_file(all_enums)
                if enum_file:
                    files.append(enum_file)

            # Generate main client.go
            files.append(self.client_gen.generate_main_client_file(ops_by_tag))

            # Generate supporting files in shared/ package to avoid circular imports
            files.append(self.files_gen.generate_errors_file(shared=True))
            files.append(self.files_gen.generate_middleware_file())
            files.append(self.files_gen.generate_validation_file())

            if self.generate_package_files:
                files.append(self.files_gen.generate_go_mod())
                files.append(self.files_gen.generate_readme())
                files.append(self.files_gen.generate_makefile())
        else:
            # Flat structure
            files.append(self.models_gen.generate_models_file())

            enum_schemas = self.get_enum_schemas()
            if enum_schemas:
                enum_file = self.models_gen.generate_enums_file()
                if enum_file:
                    files.append(enum_file)

            files.append(self.client_gen.generate_client_file())
            files.append(self.files_gen.generate_errors_file())
            files.append(self.files_gen.generate_middleware_file())
            files.append(self.files_gen.generate_validation_file())

            if self.generate_package_files:
                files.append(self.files_gen.generate_go_mod())
                files.append(self.files_gen.generate_readme())
                files.append(self.files_gen.generate_makefile())

        # Generate CLAUDE.md
        files.append(ClaudeGenerator(self.context, "go", group_name=self.group_name).generate())

        return files

    def _generate_app_folder(self, tag: str, operations: list[IROperationObject]) -> list[GeneratedFile]:
        """Generate folder for a specific app (tag)."""
        files = []

        # Get schemas used by this app
        app_schemas = self._get_schemas_for_operations(operations)

        # Generate models.go for this app
        models_file = self.models_gen.generate_app_models_file(tag, app_schemas, operations)
        if models_file:
            files.append(models_file)

        # Generate client.go with HTTP operations for this app
        client_file = self.client_gen.generate_subpackage_client_file(tag, operations)
        if client_file:
            files.append(client_file)

        return files

    def _get_schemas_for_operations(self, operations: list[IROperationObject]) -> dict[str, IRSchemaObject]:
        """Get all schemas used by given operations, including nested dependencies."""
        schemas = {}
        schemas_to_process = set()

        # Collect top-level schemas from operations
        for operation in operations:
            # Request body schemas
            if operation.request_body and operation.request_body.schema_name:
                schemas_to_process.add(operation.request_body.schema_name)

            # Patch request body schemas
            if operation.patch_request_body and operation.patch_request_body.schema_name:
                schemas_to_process.add(operation.patch_request_body.schema_name)

            # Response schemas
            for status_code, response in operation.responses.items():
                if response.schema_name:
                    schemas_to_process.add(response.schema_name)

        # Recursively collect all dependencies
        processed = set()
        while schemas_to_process:
            schema_name = schemas_to_process.pop()
            if schema_name in processed or schema_name not in self.context.schemas:
                continue

            processed.add(schema_name)
            schema = self.context.schemas[schema_name]
            schemas[schema_name] = schema

            # Find nested schema references
            if schema.properties:
                for prop_name, prop_schema in schema.properties.items():
                    # Direct reference to another schema
                    if prop_schema.ref and prop_schema.ref in self.context.schemas:
                        schemas_to_process.add(prop_schema.ref)

                    # Array items reference
                    if prop_schema.items and prop_schema.items.ref:
                        if prop_schema.items.ref in self.context.schemas:
                            schemas_to_process.add(prop_schema.items.ref)

        return schemas

    def _create_generated_file(self, path: str, content: str, description: str) -> GeneratedFile:
        """Create GeneratedFile instance."""
        return GeneratedFile(path=path, content=content, description=description)

    # Backward compatibility - delegate to sub-generators
    def generate_schema(self, schema: IRSchemaObject) -> str:
        """Generate Go struct for schema (delegates to ModelsGenerator)."""
        return self.models_gen.generate_schema(schema)

    def generate_enum(self, schema: IRSchemaObject) -> str:
        """Generate enum type (not directly supported, returns empty)."""
        return ""  # Go enums are handled differently

    def generate_operation(self, operation: IROperationObject, remove_tag_prefix: bool = False) -> str:
        """Generate method for operation (for compatibility)."""
        op_method = self.operations_gen.generate_operation_method(operation, remove_tag_prefix)
        return f"func (c *Client) {op_method['name']}(...) (...) {{ ... }}"
