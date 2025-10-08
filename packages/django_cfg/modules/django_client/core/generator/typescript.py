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

from .base import BaseGenerator, GeneratedFile
from ..ir import IROperationObject, IRSchemaObject


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
                files.append(self._generate_shared_enums_file(all_enums))

            # Generate main client.ts
            files.append(self._generate_main_client_file(ops_by_tag))

            # Generate main index.ts
            files.append(self._generate_main_index_file())

            # Generate http.ts with HttpClientAdapter
            files.append(self._generate_http_adapter_file())

            # Generate errors.ts with APIError
            files.append(self._generate_errors_file())

            # Generate storage.ts with StorageAdapter
            files.append(self._generate_storage_file())

            # Generate logger.ts with Consola
            files.append(self._generate_logger_file())

            # Generate schema.ts with OpenAPI schema
            if self.openapi_schema:
                files.append(self._generate_schema_file())
        else:
            # Flat structure (original logic)
            files.append(self._generate_models_file())

            enum_schemas = self.get_enum_schemas()
            if enum_schemas:
                files.append(self._generate_enums_file())

            files.append(self._generate_client_file())
            files.append(self._generate_index_file())

            # Generate storage.ts with StorageAdapter
            files.append(self._generate_storage_file())

            # Generate logger.ts with Consola
            files.append(self._generate_logger_file())

            # Generate schema.ts with OpenAPI schema
            if self.openapi_schema:
                files.append(self._generate_schema_file())

        return files

    # ===== Models Generation =====

    def _generate_models_file(self) -> GeneratedFile:
        """Generate models.ts with all TypeScript interfaces."""
        # Generate all schemas
        schema_codes = []

        # Response models first
        for name, schema in self.get_response_schemas().items():
            schema_codes.append(self.generate_schema(schema))

        # Request models
        for name, schema in self.get_request_schemas().items():
            schema_codes.append(self.generate_schema(schema))

        # Patch models
        for name, schema in self.get_patch_schemas().items():
            schema_codes.append(self.generate_schema(schema))

        template = self.jinja_env.get_template('typescript/models/models.ts.jinja')
        content = template.render(
            has_enums=bool(self.get_enum_schemas()),
            schemas=schema_codes
        )

        return GeneratedFile(
            path="models.ts",
            content=content,
            description="TypeScript interfaces (Request/Response/Patch)",
        )

    def _generate_enums_file(self) -> GeneratedFile:
        """Generate enums.ts with all enum types (flat structure)."""
        enum_codes = []
        for name, schema in self.get_enum_schemas().items():
            enum_codes.append(self.generate_enum(schema))

        template = self.jinja_env.get_template('typescript/models/enums.ts.jinja')
        content = template.render(enums=enum_codes)

        return GeneratedFile(
            path="enums.ts",
            content=content,
            description="Enum types from x-enum-varnames",
        )

    def _generate_shared_enums_file(self, enums: dict[str, IRSchemaObject]) -> GeneratedFile:
        """Generate shared enums.ts for namespaced structure (Variant 2)."""
        enum_codes = []
        for name, schema in enums.items():
            enum_codes.append(self.generate_enum(schema))

        template = self.jinja_env.get_template('typescript/models/enums.ts.jinja')
        content = template.render(enums=enum_codes)

        return GeneratedFile(
            path="enums.ts",
            content=content,
            description="Shared enum types from x-enum-varnames",
        )

    # ===== Schema Generation =====

    def generate_schema(self, schema: IRSchemaObject) -> str:
        """Generate TypeScript interface for schema."""
        if schema.type != "object":
            # For primitive types, skip (they'll be inlined)
            return ""

        # Interface comment
        comment_lines = []
        if schema.description:
            comment_lines.extend(self.wrap_comment(schema.description, 76))

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
                lines.append(self.indent(field_line, 2))
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
            email?: string | null;
            status: Enums.StatusEnum;
        """
        # Check if this field is an enum
        if schema.enum and schema.name:
            # Use enum type from shared enums
            ts_type = f"Enums.{schema.name}"
            if schema.nullable:
                ts_type = f"{ts_type} | null"
        # Check if this field is a reference to an enum (via $ref)
        elif schema.ref and schema.ref in self.context.schemas:
            ref_schema = self.context.schemas[schema.ref]
            if ref_schema.enum:
                # This is a reference to an enum component
                ts_type = f"Enums.{schema.ref}"
                if schema.nullable:
                    ts_type = f"{ts_type} | null"
            else:
                # Regular reference
                ts_type = schema.typescript_type
        else:
            # Get TypeScript type
            ts_type = schema.typescript_type

        # Check if required
        is_required = name in required_fields

        # Optional marker
        optional_marker = "" if is_required else "?"

        # Comment
        if schema.description:
            return f"/** {schema.description} */\n{name}{optional_marker}: {ts_type};"

        return f"{name}{optional_marker}: {ts_type};"

    def generate_enum(self, schema: IRSchemaObject) -> str:
        """Generate TypeScript enum from x-enum-varnames."""
        # Enum comment
        comment_lines = []
        if schema.description:
            comment_lines.extend(self.wrap_comment(schema.description, 76))

        comment = "/**\n * " + "\n * ".join(comment_lines) + "\n */" if comment_lines else None

        # Enum members
        member_lines = []
        for var_name, value in zip(schema.enum_var_names, schema.enum):
            if isinstance(value, str):
                member_lines.append(f'{var_name} = "{value}",')
            else:
                member_lines.append(f"{var_name} = {value},")

        # Build enum
        lines = []

        if comment:
            lines.append(comment)

        lines.append(f"export enum {schema.name} {{")

        for member_line in member_lines:
            lines.append(self.indent(member_line, 2))

        lines.append("}")

        return "\n".join(lines)

    # ===== Client Generation =====

    def _generate_client_file(self) -> GeneratedFile:
        """Generate client.ts with APIClient class."""
        # Client class
        client_code = self._generate_client_class()

        template = self.jinja_env.get_template('typescript/client_file.ts.jinja')
        content = template.render(
            has_enums=bool(self.get_enum_schemas()),
            client_code=client_code
        )

        return GeneratedFile(
            path="client.ts",
            content=content,
            description="APIClient with HTTP adapter and error handling",
        )

    def _generate_client_class(self) -> str:
        """Generate APIClient class."""
        if self.client_structure == "namespaced":
            return self._generate_namespaced_client()
        else:
            return self._generate_flat_client()

    def _generate_flat_client(self) -> str:
        """Generate flat APIClient (all methods in one class)."""
        # Generate all operation methods
        method_codes = []
        for op_id, operation in self.context.operations.items():
            method_codes.append(self.generate_operation(operation))

        template = self.jinja_env.get_template('typescript/client/flat_client.ts.jinja')
        return template.render(
            api_title=self.context.openapi_info.title,
            operations=method_codes
        )

    def _generate_namespaced_client(self) -> str:
        """Generate namespaced APIClient (sub-clients per tag)."""
        # Group operations by tag (using base class method)
        ops_by_tag = self.group_operations_by_tag()

        # Generate sub-client classes
        sub_client_classes = []
        for tag, operations in sorted(ops_by_tag.items()):
            sub_client_classes.append(self._generate_sub_client_class(tag, operations))

        sub_clients_code = "\n\n".join(sub_client_classes)

        # Generate main APIClient
        main_client_code = self._generate_main_client_class(list(ops_by_tag.keys()))

        return f"{sub_clients_code}\n\n{main_client_code}"

    def _generate_sub_client_class(self, tag: str, operations: list) -> str:
        """Generate sub-client class for a specific tag."""
        class_name = self.tag_to_class_name(tag)

        # Generate methods for this tag
        method_codes = []
        for operation in operations:
            method_codes.append(self.generate_operation(operation, remove_tag_prefix=True, in_subclient=True))

        template = self.jinja_env.get_template('typescript/client/sub_client.ts.jinja')
        return template.render(
            tag=self.tag_to_display_name(tag),
            class_name=class_name,
            operations=method_codes
        )

    def _generate_main_client_class(self, ops_by_tag: dict) -> str:
        """Generate main APIClient with sub-clients."""
        tags = sorted(ops_by_tag.keys())

        # Prepare data for template
        tags_data = [
            {
                "class_name": self.tag_to_class_name(tag),
                "property": self.tag_to_property_name(tag),
                "slug": self.tag_and_app_to_folder_name(tag, ops_by_tag[tag]),
            }
            for tag in tags
        ]

        template = self.jinja_env.get_template('typescript/client/client.ts.jinja')
        return template.render(
            sub_clients=True,
            include_imports=False,  # Imports already in main_client_file.ts.jinja
            tags=tags_data,
            info={"title": self.context.openapi_info.title},
        )

    def generate_operation(self, operation: IROperationObject, remove_tag_prefix: bool = False, in_subclient: bool = False) -> str:
        """Generate async method for operation."""
        # Get method name
        operation_id = operation.operation_id
        if remove_tag_prefix and operation.tags:
            # Remove tag prefix using base class method
            tag = operation.tags[0]
            operation_id = self.remove_tag_prefix(operation_id, tag)

        # Convert snake_case to camelCase
        method_name = self._to_camel_case(operation_id)

        # Request method prefix
        request_prefix = "this.client" if in_subclient else "this"

        # Method parameters
        params = []

        # Add path parameters
        for param in operation.path_parameters:
            param_type = self._map_param_type(param.schema_type)
            params.append(f"{param.name}: {param_type}")

        # Check if this is a file upload operation
        is_multipart = (
            operation.request_body
            and operation.request_body.content_type == "multipart/form-data"
        )

        # Add request body parameter
        if operation.request_body:
            if is_multipart:
                # For multipart, get schema properties and add as individual File parameters
                schema_name = operation.request_body.schema_name
                if schema_name in self.context.schemas:
                    schema = self.context.schemas[schema_name]
                    for prop_name, prop in schema.properties.items():
                        # Check if it's a file field (format: binary)
                        if prop.format == "binary":
                            params.append(f"{prop_name}: File | Blob")
                        else:
                            # Regular field in multipart
                            prop_type = self._map_param_type(prop.type)
                            if prop_name in schema.required:
                                params.append(f"{prop_name}: {prop_type}")
                            else:
                                params.append(f"{prop_name}?: {prop_type}")
            else:
                # JSON request body
                params.append(f"data: Models.{operation.request_body.schema_name}")
        elif operation.patch_request_body:
            params.append(f"data?: Models.{operation.patch_request_body.schema_name}")

        # Add query parameters
        for param in operation.query_parameters:
            param_type = self._map_param_type(param.schema_type)
            if not param.required:
                param_type = f"{param_type} | null"
                params.append(f"{param.name}?: {param_type}")
            else:
                params.append(f"{param.name}: {param_type}")

        # Return type
        primary_response = operation.primary_success_response
        if primary_response and primary_response.schema_name:
            if operation.is_list_operation:
                return_type = f"Models.{primary_response.schema_name}[]"
            else:
                return_type = f"Models.{primary_response.schema_name}"
        else:
            return_type = "void"

        signature = f"async {method_name}({', '.join(params)}): Promise<{return_type}> {{"

        # Comment
        comment_lines = []
        if operation.summary:
            comment_lines.append(operation.summary)
        if operation.description:
            if comment_lines:
                comment_lines.append("")
            comment_lines.extend(self.wrap_comment(operation.description, 72))

        comment = "/**\n * " + "\n * ".join(comment_lines) + "\n */" if comment_lines else None

        # Method body
        body_lines = []

        # Build path
        path_expr = f'"{operation.path}"'
        if operation.path_parameters:
            # Replace {id} with ${id}
            path_with_vars = operation.path
            for param in operation.path_parameters:
                path_with_vars = path_with_vars.replace(f"{{{param.name}}}", f"${{{param.name}}}")
            path_expr = f'`{path_with_vars}`'

        # Build request options
        request_opts = []

        # Query params
        if operation.query_parameters:
            query_items = [f"{param.name}" for param in operation.query_parameters]
            query_dict = "{ " + ", ".join(query_items) + " }"
            request_opts.append(f"params: {query_dict}")

        # Body / FormData
        if operation.request_body or operation.patch_request_body:
            if is_multipart and operation.request_body:
                # Build FormData for multipart upload
                schema_name = operation.request_body.schema_name
                if schema_name in self.context.schemas:
                    schema = self.context.schemas[schema_name]
                    body_lines.append("const formData = new FormData();")
                    for prop_name, prop in schema.properties.items():
                        if prop.format == "binary":
                            # Append file
                            body_lines.append(f"formData.append('{prop_name}', {prop_name});")
                        elif prop_name in schema.required or True:  # Append all non-undefined fields
                            # Append other fields (wrap in if check for optional)
                            if prop_name not in schema.required:
                                body_lines.append(f"if ({prop_name} !== undefined) formData.append('{prop_name}', String({prop_name}));")
                            else:
                                body_lines.append(f"formData.append('{prop_name}', String({prop_name}));")
                    request_opts.append("formData")
            else:
                # JSON body
                request_opts.append("body: data")

        # Make request
        if request_opts:
            request_line = f"const response = await {request_prefix}.request<{return_type}>('{operation.http_method}', {path_expr}, {{ {', '.join(request_opts)} }});"
        else:
            request_line = f"const response = await {request_prefix}.request<{return_type}>('{operation.http_method}', {path_expr});"

        body_lines.append(request_line)

        # Handle response
        if operation.is_list_operation and primary_response:
            # Extract results from paginated response
            body_lines.append("return (response as any).results || [];")
        elif return_type != "void":
            body_lines.append("return response;")
        else:
            body_lines.append("return;")

        # Build method
        lines = []

        if comment:
            lines.append(comment)

        lines.append(signature)

        for line in body_lines:
            lines.append(self.indent(line, 2))

        lines.append("}")

        return "\n".join(lines)

    def _map_param_type(self, schema_type: str) -> str:
        """Map parameter schema type to TypeScript type."""
        type_map = {
            "string": "string",
            "integer": "number",
            "number": "number",
            "boolean": "boolean",
            "array": "any[]",
        }
        return type_map.get(schema_type, "any")

    def _to_camel_case(self, snake_str: str) -> str:
        """
        Convert snake_case to camelCase.

        Examples:
            >>> self._to_camel_case("users_list")
            'usersList'
            >>> self._to_camel_case("users_partial_update")
            'usersPartialUpdate'
        """
        components = snake_str.split("_")
        return components[0] + "".join(x.title() for x in components[1:])

    # ===== Index File =====

    def _generate_index_file(self) -> GeneratedFile:
        """Generate index.ts with exports."""
        template = self.jinja_env.get_template('typescript/index.ts.jinja')
        content = template.render(
            has_enums=bool(self.get_enum_schemas())
        )

        return GeneratedFile(
            path="index.ts",
            content=content,
            description="Module exports",
        )

    # ===== Per-App Folder Generation (Namespaced Structure) =====

    def _generate_app_folder(self, tag: str, operations: list[IROperationObject]) -> list[GeneratedFile]:
        """Generate folder for a specific app (tag)."""
        files = []

        # Get schemas used by this app
        app_schemas = self._get_schemas_for_operations(operations)

        # Generate models.ts for this app
        files.append(self._generate_app_models_file(tag, app_schemas, operations))

        # Generate client.ts for this app
        files.append(self._generate_app_client_file(tag, operations))

        # Generate index.ts for this app
        files.append(self._generate_app_index_file(tag, operations))

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

            # Check array items for $ref at schema level
            if schema.items and schema.items.ref:
                if schema.items.ref not in seen:
                    if schema.items.ref in self.context.schemas:
                        resolved[schema.items.ref] = self.context.schemas[schema.items.ref]
                        queue.append(self.context.schemas[schema.items.ref])
                        seen.add(schema.items.ref)

        return resolved

    def _generate_app_models_file(self, tag: str, schemas: dict[str, IRSchemaObject], operations: list[IROperationObject]) -> GeneratedFile:
        """Generate models.ts for a specific app."""
        # Check if we have enums in schemas
        app_enums = self._collect_enums_from_schemas(schemas)
        has_enums = len(app_enums) > 0

        # Generate schemas
        schema_codes = []
        for name, schema in schemas.items():
            schema_codes.append(self.generate_schema(schema))

        template = self.jinja_env.get_template('typescript/models/app_models.ts.jinja')
        content = template.render(
            has_enums=has_enums,
            schemas=schema_codes
        )

        folder_name = self.tag_and_app_to_folder_name(tag, operations)
        return GeneratedFile(
            path=f"{folder_name}/models.ts",
            content=content,
            description=f"TypeScript interfaces for {tag}",
        )

    def _generate_app_client_file(self, tag: str, operations: list[IROperationObject]) -> GeneratedFile:
        """Generate client.ts for a specific app."""
        class_name = self.tag_to_class_name(tag)

        # Generate methods
        method_codes = []
        for operation in operations:
            method_codes.append(self.generate_operation(operation, remove_tag_prefix=True, in_subclient=True))

        template = self.jinja_env.get_template('typescript/client/app_client.ts.jinja')
        content = template.render(
            tag=self.tag_to_display_name(tag),
            class_name=class_name,
            operations=method_codes
        )

        folder_name = self.tag_and_app_to_folder_name(tag, operations)
        return GeneratedFile(
            path=f"{folder_name}/client.ts",
            content=content,
            description=f"API client for {tag}",
        )

    def _generate_app_index_file(self, tag: str, operations: list[IROperationObject]) -> GeneratedFile:
        """Generate index.ts for a specific app."""
        template = self.jinja_env.get_template('typescript/app_index.ts.jinja')
        content = template.render()

        folder_name = self.tag_and_app_to_folder_name(tag, operations)
        return GeneratedFile(
            path=f"{folder_name}/index.ts",
            content=content,
            description=f"Module exports for {tag}",
        )

    def _generate_main_client_file(self, ops_by_tag: dict) -> GeneratedFile:
        """Generate main client.ts with APIClient."""
        tags = sorted(ops_by_tag.keys())

        # Prepare tags data for template
        tags_data = [
            {
                "class_name": self.tag_to_class_name(tag),
                "slug": self.tag_and_app_to_folder_name(tag, ops_by_tag[tag]),
            }
            for tag in tags
        ]

        # Generate main APIClient class
        client_code = self._generate_main_client_class(ops_by_tag)

        template = self.jinja_env.get_template('typescript/client/main_client_file.ts.jinja')
        content = template.render(
            tags=tags_data,
            client_code=client_code
        )

        return GeneratedFile(
            path="client.ts",
            content=content,
            description="Main API client with HTTP adapter and error handling",
        )

    def _generate_main_index_file(self) -> GeneratedFile:
        """Generate main index.ts with API class and JWT management."""
        ops_by_tag = self.group_operations_by_tag()
        tags = sorted(ops_by_tag.keys())

        # Prepare tags data for template
        tags_data = [
            {
                "class_name": self.tag_to_class_name(tag, suffix=""),
                "property": self.tag_to_property_name(tag),
                "slug": self.tag_and_app_to_folder_name(tag, ops_by_tag[tag]),
            }
            for tag in tags
        ]

        # Check if we have enums
        all_schemas = self.context.schemas
        all_enums = self._collect_enums_from_schemas(all_schemas)

        template = self.jinja_env.get_template('typescript/main_index.ts.jinja')
        content = template.render(
            api_title=self.context.openapi_info.title,
            tags=tags_data,
            has_enums=bool(all_enums)
        )

        return GeneratedFile(
            path="index.ts",
            content=content,
            description="Main index with API class and JWT management",
        )

    def _generate_http_adapter_file(self) -> GeneratedFile:
        """Generate http.ts with HttpClient adapter interface."""
        template = self.jinja_env.get_template('typescript/utils/http.ts.jinja')
        content = template.render()

        return GeneratedFile(
            path="http.ts",
            content=content,
            description="HTTP client adapter interface and implementations",
        )

    def _generate_errors_file(self) -> GeneratedFile:
        """Generate errors.ts with APIError class."""
        template = self.jinja_env.get_template('typescript/utils/errors.ts.jinja')
        content = template.render()

        return GeneratedFile(
            path="errors.ts",
            content=content,
            description="API error classes",
        )

    def _generate_storage_file(self) -> GeneratedFile:
        """Generate storage.ts with StorageAdapter implementations."""
        template = self.jinja_env.get_template('typescript/utils/storage.ts.jinja')
        content = template.render()

        return GeneratedFile(
            path="storage.ts",
            content=content,
            description="Storage adapters for cross-platform support",
        )

    def _generate_logger_file(self) -> GeneratedFile:
        """Generate logger.ts with Consola integration."""
        template = self.jinja_env.get_template('typescript/utils/logger.ts.jinja')
        content = template.render()

        return GeneratedFile(
            path="logger.ts",
            content=content,
            description="API Logger with Consola",
        )

    def _generate_schema_file(self) -> GeneratedFile:
        """Generate schema.ts with OpenAPI schema as const."""
        template = self.jinja_env.get_template('typescript/utils/schema.ts.jinja')
        content = template.render(schema=self.openapi_schema)

        return GeneratedFile(
            path="schema.ts",
            content=content,
            description="OpenAPI Schema",
        )
