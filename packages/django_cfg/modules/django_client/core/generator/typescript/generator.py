"""
TypeScript Generator - Generates TypeScript client (Fetch API).

This generator creates a complete TypeScript API client from IR:
- TypeScript interfaces (Request/Response/Patch splits)
- Enum types from x-enum-varnames
- Fetch API for HTTP
- Django CSRF/session handling
- Type-safe
"""

from __future__ import annotations

import pathlib

from jinja2 import Environment, FileSystemLoader, select_autoescape

from ...ir import IROperationObject, IRSchemaObject
from ..base import BaseGenerator, GeneratedFile
from ..claude_generator import ClaudeGenerator
from .client_generator import ClientGenerator
from .fetchers_generator import FetchersGenerator
from .files_generator import FilesGenerator
from .hooks_generator import HooksGenerator
from .models_generator import ModelsGenerator
from .operations_generator import OperationsGenerator
from .schemas_generator import SchemasGenerator
from .validator import TypeScriptValidator


class TypeScriptGenerator(BaseGenerator):
    """
    TypeScript client generator.

    Generates:
    - models.ts: TypeScript interfaces (User, UserRequest, PatchedUser)
    - enums.ts: Enum types (StatusEnum, RoleEnum)
    - client.ts: APIClient class with all operations
    - index.ts: Module exports
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
        self.operations_gen = OperationsGenerator(self.jinja_env, self.context, self)
        self.client_gen = ClientGenerator(self.jinja_env, self.context, self, self.operations_gen)
        self.files_gen = FilesGenerator(self.jinja_env, self.context, self)
        self.schemas_gen = SchemasGenerator(self.jinja_env, self.context, self)
        self.fetchers_gen = FetchersGenerator(self.jinja_env, self.context, self)
        self.hooks_gen = HooksGenerator(self.jinja_env, self.context, self)

    def generate(self) -> list[GeneratedFile]:
        """Generate all TypeScript client files."""
        files = []

        if self.client_structure == "namespaced":
            # Generate per-app folders
            ops_by_tag = self.group_operations_by_tag()

            for tag, operations in sorted(ops_by_tag.items()):
                # Generate app folder (models.ts, client.ts, index.ts)
                files.extend(self._generate_app_folder(tag, operations))

            # Generate shared enums.ts (Variant 2: all enums in root)
            all_schemas = self.context.schemas
            all_enums = self._collect_enums_from_schemas(all_schemas)
            if all_enums:
                files.append(self.models_gen.generate_shared_enums_file(all_enums))

            # Generate main client.ts
            files.append(self.client_gen.generate_main_client_file(ops_by_tag))

            # Generate main index.ts
            files.append(self.files_gen.generate_main_index_file())

            # Generate http.ts with HttpClientAdapter
            files.append(self.files_gen.generate_http_adapter_file())

            # Generate errors.ts with APIError
            files.append(self.files_gen.generate_errors_file())

            # Generate storage.ts with StorageAdapter
            files.append(self.files_gen.generate_storage_file())

            # Generate logger.ts with Consola
            files.append(self.files_gen.generate_logger_file())

            # Generate retry.ts with p-retry
            files.append(self.files_gen.generate_retry_file())

            # Generate validation-events.ts (browser CustomEvent for Zod errors)
            if self.generate_zod_schemas:
                files.append(self.files_gen.generate_validation_events_file())

            # Generate api-instance.ts singleton (needed for fetchers/hooks)
            if self.generate_fetchers:
                files.append(self.files_gen.generate_api_instance_file())

            # Generate schema.ts with OpenAPI schema
            if self.openapi_schema:
                files.append(self.files_gen.generate_schema_file())

            # Generate Zod schemas if requested
            if self.generate_zod_schemas:
                files.extend(self._generate_zod_schemas())

            # Generate fetchers if requested
            if self.generate_fetchers:
                if not self.generate_zod_schemas:
                    print("⚠️  Warning: Fetchers require Zod schemas. Enable generate_zod_schemas.")
                else:
                    files.extend(self._generate_fetchers())

            # Generate SWR hooks if requested
            if self.generate_swr_hooks:
                if not self.generate_fetchers:
                    print("⚠️  Warning: SWR hooks require fetchers. Enable generate_fetchers.")
                else:
                    files.extend(self._generate_swr_hooks())

            # Validate generated TypeScript code
            self._validate_typescript_files(files)
        else:
            # Flat structure (original logic)
            files.append(self.models_gen.generate_models_file())

            enum_schemas = self.get_enum_schemas()
            if enum_schemas:
                files.append(self.models_gen.generate_enums_file())

            files.append(self.client_gen.generate_client_file())
            files.append(self.files_gen.generate_index_file())

            # Generate storage.ts with StorageAdapter
            files.append(self.files_gen.generate_storage_file())

            # Generate logger.ts with Consola
            files.append(self.files_gen.generate_logger_file())

            # Generate retry.ts with p-retry
            files.append(self.files_gen.generate_retry_file())

            # Generate validation-events.ts (browser CustomEvent for Zod errors)
            if self.generate_zod_schemas:
                files.append(self.files_gen.generate_validation_events_file())

            # Generate api-instance.ts singleton (needed for fetchers/hooks)
            if self.generate_fetchers:
                files.append(self.files_gen.generate_api_instance_file())

            # Generate schema.ts with OpenAPI schema
            if self.openapi_schema:
                files.append(self.files_gen.generate_schema_file())

            # Generate Zod schemas if requested
            if self.generate_zod_schemas:
                files.extend(self._generate_zod_schemas())

            # Generate fetchers if requested
            if self.generate_fetchers:
                if not self.generate_zod_schemas:
                    print("⚠️  Warning: Fetchers require Zod schemas. Enable generate_zod_schemas.")
                else:
                    files.extend(self._generate_fetchers())

            # Generate SWR hooks if requested
            if self.generate_swr_hooks:
                if not self.generate_fetchers:
                    print("⚠️  Warning: SWR hooks require fetchers. Enable generate_fetchers.")
                else:
                    files.extend(self._generate_swr_hooks())

            # Validate generated TypeScript code
            self._validate_typescript_files(files)

        # Generate package files if requested
        if self.generate_package_files:
            files.append(self.files_gen.generate_package_json_file(self.package_config))
            files.append(self.files_gen.generate_tsconfig_file())

        # Generate CLAUDE.md
        claude_gen = ClaudeGenerator(
            self.context, "typescript",
            group_name=self.group_name,
            generate_swr_hooks=self.generate_swr_hooks,
        )
        files.append(claude_gen.generate())

        return files

    # ===== Delegation Methods (for backward compatibility with tests) =====

    def generate_schema(self, schema: IRSchemaObject) -> str:
        """Generate TypeScript interface for schema."""
        return self.models_gen.generate_schema(schema)

    def generate_enum(self, schema: IRSchemaObject) -> str:
        """Generate TypeScript enum from x-enum-varnames."""
        return self.models_gen.generate_enum(schema)

    def generate_operation(self, operation: IROperationObject, remove_tag_prefix: bool = False, in_subclient: bool = False) -> str:
        """Generate async method for operation."""
        return self.operations_gen.generate_operation(operation, remove_tag_prefix, in_subclient)

    def _to_camel_case(self, snake_str: str) -> str:
        """Convert snake_case to camelCase (delegate to operations generator)."""
        return self.operations_gen._to_camel_case(snake_str)

    # ===== Per-App Folder Generation (Namespaced Structure) =====

    def _generate_app_folder(self, tag: str, operations: list[IROperationObject]) -> list[GeneratedFile]:
        """Generate folder for a specific app (tag)."""
        files = []

        # Get schemas used by this app
        app_schemas = self._get_schemas_for_operations(operations)

        # Generate models.ts for this app
        files.append(self.models_gen.generate_app_models_file(tag, app_schemas, operations))

        # Generate client.ts for this app
        files.append(self.client_gen.generate_app_client_file(tag, operations))

        # Generate index.ts for this app
        files.append(self.files_gen.generate_app_index_file(tag, operations))

        return files

    def _get_schemas_for_operations(self, operations: list[IROperationObject]) -> dict[str, IRSchemaObject]:
        """
        Get all schemas used by given operations.

        This method recursively resolves all schema dependencies ($ref) to ensure
        that nested schemas (e.g., APIKeyList referenced by PaginatedAPIKeyListList)
        are included in the generated models file.
        """
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

        # Recursively resolve all nested schema dependencies
        schemas = self._resolve_nested_schemas(schemas)

        return schemas

    def _resolve_nested_schemas(self, initial_schemas: dict[str, IRSchemaObject]) -> dict[str, IRSchemaObject]:
        """
        Recursively resolve all nested schema dependencies ($ref).

        This ensures that if SchemaA references SchemaB (e.g., via a property or array items),
        SchemaB is also included in the output, even if it's not directly used in operations.

        Example:
            PaginatedAPIKeyListList has:
                results: Array<APIKeyList>  ← $ref to APIKeyList

            This method will find APIKeyList and include it.

        Args:
            initial_schemas: Schemas directly used by operations

        Returns:
            All schemas including nested dependencies
        """
        resolved = dict(initial_schemas)
        queue = list(initial_schemas.values())
        seen = set(initial_schemas.keys())

        while queue:
            schema = queue.pop(0)

            # Check properties for $ref and nested items
            if schema.properties:
                for prop in schema.properties.values():
                    # Direct $ref on property
                    if prop.ref and prop.ref not in seen:
                        if prop.ref in self.context.schemas:
                            resolved[prop.ref] = self.context.schemas[prop.ref]
                            queue.append(self.context.schemas[prop.ref])
                            seen.add(prop.ref)

                    # $ref inside array items (CRITICAL for PaginatedXList patterns!)
                    if prop.items and prop.items.ref:
                        if prop.items.ref not in seen:
                            if prop.items.ref in self.context.schemas:
                                resolved[prop.items.ref] = self.context.schemas[prop.items.ref]
                                queue.append(self.context.schemas[prop.items.ref])
                                seen.add(prop.items.ref)

                    # $ref inside additionalProperties (CRITICAL for Record<string, T> patterns!)
                    if prop.additional_properties and prop.additional_properties.ref:
                        if prop.additional_properties.ref not in seen:
                            if prop.additional_properties.ref in self.context.schemas:
                                resolved[prop.additional_properties.ref] = self.context.schemas[prop.additional_properties.ref]
                                queue.append(self.context.schemas[prop.additional_properties.ref])
                                seen.add(prop.additional_properties.ref)

            # Check array items for $ref at schema level
            if schema.items and schema.items.ref:
                if schema.items.ref not in seen:
                    if schema.items.ref in self.context.schemas:
                        resolved[schema.items.ref] = self.context.schemas[schema.items.ref]
                        queue.append(self.context.schemas[schema.items.ref])
                        seen.add(schema.items.ref)

            # Check additionalProperties for $ref at schema level
            if schema.additional_properties and schema.additional_properties.ref:
                if schema.additional_properties.ref not in seen:
                    if schema.additional_properties.ref in self.context.schemas:
                        resolved[schema.additional_properties.ref] = self.context.schemas[schema.additional_properties.ref]
                        queue.append(self.context.schemas[schema.additional_properties.ref])
                        seen.add(schema.additional_properties.ref)

        return resolved

    # ===== Zod Schemas Generation =====

    def _generate_zod_schemas(self) -> list[GeneratedFile]:
        """
        Generate Zod validation schemas for all models.

        Creates:
        - schemas/User.schema.ts
        - schemas/UserRequest.schema.ts
        - schemas/PaginatedUser.schema.ts
        - schemas/index.ts
        """
        files = []
        schema_names = []

        # Get all schemas that should have Zod validation
        all_schemas = {**self.context.schemas}

        # Track refs to resolve dependencies
        schema_refs = {}  # schema_name -> set of referenced schemas
        for schema_name, schema in all_schemas.items():
            refs = self._get_schema_refs(schema)
            schema_refs[schema_name] = refs

        # Generate individual schema files
        for schema_name, schema in sorted(all_schemas.items()):
            # Skip enum schemas (they use z.enum() with literal values)
            if schema.enum:
                continue

            # Generate Zod schema file
            refs = schema_refs.get(schema_name, set())
            files.append(self.schemas_gen.generate_schema_file(schema, refs))
            schema_names.append(schema_name)

        # Generate index.ts
        if schema_names:
            files.append(self.schemas_gen.generate_schemas_index_file(schema_names))

        return files

    def _get_schema_refs(self, schema: IRSchemaObject) -> set[str]:
        """
        Get all schemas referenced by this schema.

        Returns set of schema names that are directly referenced.
        """
        refs = set()

        if schema.properties:
            for prop in schema.properties.values():
                if prop.ref and prop.ref in self.context.schemas:
                    # Don't include enum refs (they're handled separately)
                    if not self.context.schemas[prop.ref].enum:
                        refs.add(prop.ref)

                if prop.items and prop.items.ref:
                    if prop.items.ref in self.context.schemas:
                        if not self.context.schemas[prop.items.ref].enum:
                            refs.add(prop.items.ref)

                if prop.additional_properties and prop.additional_properties.ref:
                    if prop.additional_properties.ref in self.context.schemas:
                        if not self.context.schemas[prop.additional_properties.ref].enum:
                            refs.add(prop.additional_properties.ref)

        if schema.items and schema.items.ref:
            if schema.items.ref in self.context.schemas:
                if not self.context.schemas[schema.items.ref].enum:
                    refs.add(schema.items.ref)

        if schema.additional_properties and schema.additional_properties.ref:
            if schema.additional_properties.ref in self.context.schemas:
                if not self.context.schemas[schema.additional_properties.ref].enum:
                    refs.add(schema.additional_properties.ref)

        return refs

    # ===== Fetchers Generation =====

    def _generate_fetchers(self) -> list[GeneratedFile]:
        """
        Generate typed fetcher functions for all operations.

        Creates:
        - _utils/fetchers/users.ts
        - _utils/fetchers/posts.ts
        - _utils/fetchers/index.ts
        """
        files = []
        module_names = []

        # Group operations by tag
        ops_by_tag = self.group_operations_by_tag()

        # Generate fetchers for each tag
        for tag, operations in sorted(ops_by_tag.items()):
            folder_name = self.tag_and_app_to_folder_name(tag, operations)

            # Generate fetchers file for this tag
            files.append(self.fetchers_gen.generate_tag_fetchers_file(tag, operations))
            module_names.append(folder_name)

        # Generate index.ts
        if module_names:
            files.append(self.fetchers_gen.generate_fetchers_index_file(module_names))

        return files

    # ===== SWR Hooks Generation =====

    def _generate_swr_hooks(self) -> list[GeneratedFile]:
        """
        Generate SWR hooks for all operations.

        Creates:
        - _utils/hooks/shop_products.ts
        - _utils/hooks/shop_orders.ts
        - _utils/hooks/index.ts
        """
        files = []
        module_names = []

        # Group operations by tag
        ops_by_tag = self.group_operations_by_tag()

        # Generate hooks for each tag
        for tag, operations in sorted(ops_by_tag.items()):
            folder_name = self.tag_and_app_to_folder_name(tag, operations)

            # Generate hooks file for this tag
            files.append(self.hooks_gen.generate_tag_hooks_file(tag, operations))
            module_names.append(folder_name)

        # Generate index.ts
        if module_names:
            files.append(self.hooks_gen.generate_hooks_index_file(module_names))

        return files

    # ===== TypeScript Validation =====

    def _validate_typescript_files(self, files: list[GeneratedFile]) -> None:
        """
        Validate generated TypeScript files for common errors.

        This method performs fast regex-based checks on generated TypeScript code
        to catch common issues before they cause compilation errors:
        - Required parameters after optional parameters
        - Required fields in optional objects
        - Invalid TypeScript syntax patterns

        Args:
            files: List of generated files to validate

        Raises:
            SystemExit: If validation errors are found (stops generation)
        """
        validator = TypeScriptValidator()
        all_errors = {}

        # Validate only TypeScript files
        for file in files:
            if file.path.endswith('.ts'):
                errors = validator.validate_file(file.path, file.content)
                if errors:
                    all_errors[file.path] = errors

        # If errors found, print and exit
        if all_errors:
            print("\n" + "=" * 60)
            print("⚠️  TypeScript Validation Errors Found")
            print("=" * 60)

            total_errors = 0
            for file_path, errors in all_errors.items():
                print(f"\n📄 {file_path}")
                for error in errors:
                    print(f"   {error}")
                    total_errors += 1

            print("\n" + "=" * 60)
            print(f"❌ Found {total_errors} validation error(s) in {len(all_errors)} file(s)")
            print("=" * 60 + "\n")

            # Exit to prevent writing invalid files
            import sys
            sys.exit(1)

        # Success - no errors found
        print("✅ TypeScript validation passed")
