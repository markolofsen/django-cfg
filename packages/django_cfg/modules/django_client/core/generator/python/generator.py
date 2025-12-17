"""
Python Generator - Main orchestrator for Python client generation.

Coordinates all sub-generators:
- ModelsGenerator: Pydantic models and enums
- OperationsGenerator: Operation methods (async/sync)
- AsyncClientGenerator: Async client classes
- SyncClientGenerator: Sync client classes
- FilesGenerator: Auxiliary files (__init__.py, logger, schema)
"""

from __future__ import annotations

import pathlib

from jinja2 import Environment, FileSystemLoader, select_autoescape

from ...ir import IROperationObject, IRSchemaObject
from ..base import BaseGenerator, GeneratedFile
from ..claude_generator import ClaudeGenerator
from .async_client_gen import AsyncClientGenerator
from .files_generator import FilesGenerator
from .models_generator import ModelsGenerator
from .operations_generator import OperationsGenerator
from .sync_client_gen import SyncClientGenerator


class PythonGenerator(BaseGenerator):
    """
    Python client generator.

    Generates:
    - models.py: Pydantic 2 models (User, UserRequest, PatchedUser)
    - enums.py: Enum classes (StatusEnum, RoleEnum)
    - client.py: AsyncClient with all operations
    - sync_client.py: SyncClient with all operations
    - __init__.py: Package exports
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

        # Initialize sub-generators
        self.models_gen = ModelsGenerator(self.jinja_env, self.context, self)
        self.operations_gen = OperationsGenerator(self.jinja_env, self)
        self.async_client_gen = AsyncClientGenerator(self.jinja_env, self.context, self, self.operations_gen)
        self.sync_client_gen = SyncClientGenerator(self.jinja_env, self, self.operations_gen)
        self.files_gen = FilesGenerator(self.jinja_env, self.context, self)

    def generate(self) -> list[GeneratedFile]:
        """Generate all Python client files."""
        files = []

        if self.client_structure == "namespaced":
            # Generate per-app folders
            ops_by_tag = self.group_operations_by_tag()

            for tag, operations in sorted(ops_by_tag.items()):
                # Generate app folder (models.py, client.py, sync_client.py, __init__.py)
                files.extend(self._generate_app_folder(tag, operations))

            # Generate shared enums.py (Variant 2: all enums in root)
            all_schemas = self.context.schemas
            all_enums = self._collect_enums_from_schemas(all_schemas)
            if all_enums:
                files.append(self.models_gen.generate_shared_enums_file(all_enums))

            # Generate main async client.py
            files.append(self.async_client_gen.generate_main_client_file(ops_by_tag))

            # Generate main sync client.py
            files.append(self.sync_client_gen.generate_sync_main_client_file(ops_by_tag))

            # Generate main __init__.py
            files.append(self.files_gen.generate_main_init_file())

            # Generate logger.py with Rich
            files.append(self.files_gen.generate_logger_file())

            # Generate retry.py with tenacity
            files.append(self.files_gen.generate_retry_file())

            # Generate schema.py with OpenAPI schema
            if self.openapi_schema:
                files.append(self.files_gen.generate_schema_file(self.openapi_schema))
        else:
            # Flat structure (original logic)
            files.append(self.models_gen.generate_models_file())

            enum_schemas = self.get_enum_schemas()
            if enum_schemas:
                files.append(self.models_gen.generate_enums_file())

            files.append(self.async_client_gen.generate_client_file())
            files.append(self.files_gen.generate_init_file())

            # Generate logger.py with Rich
            files.append(self.files_gen.generate_logger_file())

            # Generate retry.py with tenacity
            files.append(self.files_gen.generate_retry_file())

            # Generate schema.py with OpenAPI schema
            if self.openapi_schema:
                files.append(self.files_gen.generate_schema_file(self.openapi_schema))

        # Generate package files if requested
        if self.generate_package_files:
            files.append(self.files_gen.generate_pyproject_toml_file(self.package_config))

        # Generate CLAUDE.md
        files.append(ClaudeGenerator(self.context, "python", group_name=self.group_name).generate())

        return files

    def _generate_app_folder(self, tag: str, operations: list[IROperationObject]) -> list[GeneratedFile]:
        """Generate folder for a specific app (tag)."""
        files = []

        # Get schemas used by this app
        app_schemas = self._get_schemas_for_operations(operations)

        # Generate models.py for this app
        files.append(self.models_gen.generate_app_models_file(tag, app_schemas, operations))

        # Generate async client.py for this app
        files.append(self.async_client_gen.generate_app_client_file(tag, operations))

        # Generate sync client.py for this app
        files.append(self.sync_client_gen.generate_app_sync_client_file(tag, operations))

        # Generate __init__.py for this app
        files.append(self.files_gen.generate_app_init_file(tag, operations))

        return files

    def _get_schemas_for_operations(self, operations: list[IROperationObject]) -> dict[str, IRSchemaObject]:
        """Get all schemas used by given operations."""
        schemas = {}

        for operation in operations:
            # Request body schemas
            if operation.request_body and operation.request_body.schema_name:
                schema_name = operation.request_body.schema_name
                if schema_name in self.context.schemas:
                    schemas[schema_name] = self.context.schemas[schema_name]

            # Patch request body schemas
            if operation.patch_request_body and operation.patch_request_body.schema_name:
                schema_name = operation.patch_request_body.schema_name
                if schema_name in self.context.schemas:
                    schemas[schema_name] = self.context.schemas[schema_name]

            # Response schemas
            for status_code, response in operation.responses.items():
                if response.schema_name:
                    if response.schema_name in self.context.schemas:
                        schemas[response.schema_name] = self.context.schemas[response.schema_name]

        return schemas

    # Backward compatibility - delegate to sub-generators
    def generate_schema(self, schema: IRSchemaObject) -> str:
        """Generate Pydantic model for schema (delegates to ModelsGenerator)."""
        return self.models_gen.generate_schema(schema)

    def generate_enum(self, schema: IRSchemaObject) -> str:
        """Generate Enum class (delegates to ModelsGenerator)."""
        return self.models_gen.generate_enum(schema)

    def generate_operation(self, operation: IROperationObject, remove_tag_prefix: bool = False) -> str:
        """Generate async method for operation (delegates to OperationsGenerator)."""
        return self.operations_gen.generate_async_operation(operation, remove_tag_prefix)

    def generate_sync_operation(self, operation: IROperationObject, remove_tag_prefix: bool = False) -> str:
        """Generate sync method for operation (delegates to OperationsGenerator)."""
        return self.operations_gen.generate_sync_operation(operation, remove_tag_prefix)
