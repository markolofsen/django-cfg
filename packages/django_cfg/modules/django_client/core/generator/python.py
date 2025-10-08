"""
Python Generator - Generates Python client (Pydantic 2 + httpx).

This generator creates a complete Python API client from IR:
- Pydantic 2 models (Request/Response/Patch splits)
- Enum classes from x-enum-varnames
- httpx.AsyncClient for async HTTP
- Django CSRF/session handling
- Type-safe (MyPy strict mode compatible)

Reference: https://docs.pydantic.dev/latest/
"""

from __future__ import annotations

import pathlib
from jinja2 import Environment, FileSystemLoader, select_autoescape

from .base import BaseGenerator, GeneratedFile
from ..ir import IROperationObject, IRSchemaObject


class PythonGenerator(BaseGenerator):
    """
    Python client generator.

    Generates:
    - models.py: Pydantic 2 models (User, UserRequest, PatchedUser)
    - enums.py: Enum classes (StatusEnum, RoleEnum)
    - client.py: AsyncClient with all operations
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

    def generate(self) -> list[GeneratedFile]:
        """Generate all Python client files."""
        files = []

        if self.client_structure == "namespaced":
            # Generate per-app folders
            ops_by_tag = self.group_operations_by_tag()

            for tag, operations in sorted(ops_by_tag.items()):
                # Generate app folder (models.py, client.py, __init__.py)
                files.extend(self._generate_app_folder(tag, operations))

            # Generate shared enums.py (Variant 2: all enums in root)
            all_schemas = self.context.schemas
            all_enums = self._collect_enums_from_schemas(all_schemas)
            if all_enums:
                files.append(self._generate_shared_enums_file(all_enums))

            # Generate main client.py
            files.append(self._generate_main_client_file(ops_by_tag))

            # Generate main __init__.py
            files.append(self._generate_main_init_file())

            # Generate logger.py with Rich
            files.append(self._generate_logger_file())

            # Generate schema.py with OpenAPI schema
            if self.openapi_schema:
                files.append(self._generate_schema_file())
        else:
            # Flat structure (original logic)
            files.append(self._generate_models_file())

            enum_schemas = self.get_enum_schemas()
            if enum_schemas:
                files.append(self._generate_enums_file())

            files.append(self._generate_client_file())
            files.append(self._generate_init_file())

            # Generate logger.py with Rich
            files.append(self._generate_logger_file())

            # Generate schema.py with OpenAPI schema
            if self.openapi_schema:
                files.append(self._generate_schema_file())

        return files

    # ===== Models Generation =====

    def _generate_models_file(self) -> GeneratedFile:
        """Generate models.py with all Pydantic models."""
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

        template = self.jinja_env.get_template('python/models/models.py.jinja')
        content = template.render(
            has_enums=bool(self.get_enum_schemas()),
            schemas=schema_codes
        )

        return GeneratedFile(
            path="models.py",
            content=content,
            description="Pydantic 2 models (Request/Response/Patch)",
        )

    def _generate_enums_file(self) -> GeneratedFile:
        """Generate enums.py with all Enum classes (flat structure)."""
        # Generate all enums
        enum_codes = []
        for name, schema in self.get_enum_schemas().items():
            enum_codes.append(self.generate_enum(schema))

        template = self.jinja_env.get_template('python/models/enums.py.jinja')
        content = template.render(enums=enum_codes)

        return GeneratedFile(
            path="enums.py",
            content=content,
            description="Enum classes from x-enum-varnames",
        )

    def _generate_shared_enums_file(self, enums: dict[str, IRSchemaObject]) -> GeneratedFile:
        """Generate shared enums.py for namespaced structure (Variant 2)."""
        # Generate all enums
        enum_codes = []
        for name, schema in enums.items():
            enum_codes.append(self.generate_enum(schema))

        template = self.jinja_env.get_template('python/models/enums.py.jinja')
        content = template.render(enums=enum_codes)

        return GeneratedFile(
            path="enums.py",
            content=content,
            description="Shared enum classes from x-enum-varnames",
        )

    # ===== Schema Generation =====

    def generate_schema(self, schema: IRSchemaObject) -> str:
        """Generate Pydantic model for schema."""
        if schema.type != "object":
            # For primitive types, skip (they'll be inlined)
            return ""

        # Class docstring
        docstring_lines = []
        if schema.description:
            docstring_lines.extend(self.wrap_comment(schema.description, 76))

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

        template = self.jinja_env.get_template('python/models/schema_class.py.jinja')
        return template.render(
            name=schema.name,
            docstring=docstring,
            fields=field_lines
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
            # Use enum type from shared enums
            python_type = schema.name
            if schema.nullable:
                python_type = f"{python_type} | None"
        # Check if this field is a reference to an enum (via $ref)
        elif schema.ref and schema.ref in self.context.schemas:
            ref_schema = self.context.schemas[schema.ref]
            if ref_schema.enum:
                # This is a reference to an enum component
                python_type = schema.ref
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
            field_kwargs.append(f"ge={schema.minimum}")
        if schema.maximum is not None:
            field_kwargs.append(f"le={schema.maximum}")

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

        # Class docstring
        docstring_lines = []
        if schema.description:
            docstring_lines.extend(self.wrap_comment(schema.description, 76))

        docstring = "\n".join(docstring_lines) if docstring_lines else None

        # Enum members
        member_lines = []
        for var_name, value in zip(schema.enum_var_names, schema.enum):
            if isinstance(value, str):
                member_lines.append(f'{var_name} = "{value}"')
            else:
                member_lines.append(f"{var_name} = {value}")

        template = self.jinja_env.get_template('python/models/enum_class.py.jinja')
        return template.render(
            name=schema.name,
            base_class=base_class,
            docstring=docstring,
            members=member_lines
        )

    # ===== Client Generation =====

    def _generate_client_file(self) -> GeneratedFile:
        """Generate client.py with AsyncClient."""
        # Client class
        client_code = self._generate_client_class()

        template = self.jinja_env.get_template('python/client_file.py.jinja')
        content = template.render(
            has_enums=bool(self.get_enum_schemas()),
            client_code=client_code
        )

        return GeneratedFile(
            path="client.py",
            content=content,
            description="AsyncClient with httpx",
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

        template = self.jinja_env.get_template('python/client/flat_client.py.jinja')
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

        sub_clients_code = "\n\n\n".join(sub_client_classes)

        # Generate main APIClient
        main_client_code = self._generate_main_client_class(ops_by_tag)

        return f"{sub_clients_code}\n\n\n{main_client_code}"

    def _generate_sub_client_class(self, tag: str, operations: list) -> str:
        """Generate sub-client class for a specific tag."""
        class_name = self.tag_to_class_name(tag)

        # Generate methods for this tag
        method_codes = []
        for operation in operations:
            method_codes.append(self.generate_operation(operation, remove_tag_prefix=True))

        template = self.jinja_env.get_template('python/client/sub_client.py.jinja')
        return template.render(
            tag=self.tag_to_display_name(tag),
            class_name=class_name,
            operations=method_codes
        )

    def _generate_main_client_class(self, ops_by_tag: dict) -> str:
        """Generate main APIClient with sub-clients."""
        tags = sorted(ops_by_tag.keys())

        # Prepare tags data for template
        tags_data = [
            {
                "class_name": self.tag_to_class_name(tag),
                "property": self.tag_to_property_name(tag),
            }
            for tag in tags
        ]

        template = self.jinja_env.get_template('python/client/main_client.py.jinja')
        return template.render(
            api_title=self.context.openapi_info.title,
            tags=tags_data
        )

    def generate_operation(self, operation: IROperationObject, remove_tag_prefix: bool = False) -> str:
        """Generate async method for operation."""
        # Get method name
        method_name = operation.operation_id
        if remove_tag_prefix and operation.tags:
            # Remove tag prefix using base class method
            tag = operation.tags[0]
            method_name = self.remove_tag_prefix(method_name, tag)

        # Method signature
        params = ["self"]

        # Add path parameters
        for param in operation.path_parameters:
            param_type = self._map_param_type(param.schema_type)
            params.append(f"{param.name}: {param_type}")

        # Add request body parameter
        if operation.request_body:
            params.append(f"data: {operation.request_body.schema_name}")
        elif operation.patch_request_body:
            params.append(f"data: {operation.patch_request_body.schema_name} | None = None")

        # Add query parameters
        for param in operation.query_parameters:
            param_type = self._map_param_type(param.schema_type)
            if not param.required:
                param_type = f"{param_type} | None = None"
            params.append(f"{param.name}: {param_type}")

        # Return type
        primary_response = operation.primary_success_response
        if primary_response and primary_response.schema_name:
            if operation.is_list_operation:
                return_type = f"list[{primary_response.schema_name}]"
            else:
                return_type = primary_response.schema_name
        else:
            return_type = "None"

        signature = f"async def {method_name}({', '.join(params)}) -> {return_type}:"

        # Docstring
        docstring_lines = []
        if operation.summary:
            docstring_lines.append(operation.summary)
        if operation.description:
            if docstring_lines:
                docstring_lines.append("")
            docstring_lines.extend(self.wrap_comment(operation.description, 72))

        docstring = "\n".join(docstring_lines) if docstring_lines else None

        # Method body
        body_lines = []

        # Build URL
        url_expr = f'"{operation.path}"'
        if operation.path_parameters:
            # Replace {id} with f-string {id}
            url_expr = f'f"{operation.path}"'

        body_lines.append(f"url = {url_expr}")

        # Build request
        request_kwargs = []

        # Query params
        if operation.query_parameters:
            query_items = []
            for param in operation.query_parameters:
                if param.required:
                    query_items.append(f'"{param.name}": {param.name}')
                else:
                    query_items.append(f'"{param.name}": {param.name} if {param.name} is not None else None')

            query_dict = "{" + ", ".join(query_items) + "}"
            request_kwargs.append(f"params={query_dict}")

        # JSON body
        if operation.request_body or operation.patch_request_body:
            request_kwargs.append("json=data.model_dump() if data else None")

        # Make request
        method_lower = operation.http_method.lower()
        request_line = f"response = await self._client.{method_lower}(url"
        if request_kwargs:
            request_line += ", " + ", ".join(request_kwargs)
        request_line += ")"

        body_lines.append(request_line)

        # Handle response
        body_lines.append("response.raise_for_status()")

        if return_type != "None":
            if operation.is_list_operation:
                # Paginated list response - extract results
                body_lines.append(f"data = response.json()")
                body_lines.append(f'return [{ primary_response.schema_name}.model_validate(item) for item in data.get("results", [])]')
            else:
                body_lines.append(f"return {primary_response.schema_name}.model_validate(response.json())")
        else:
            body_lines.append("return None")

        template = self.jinja_env.get_template('python/client/operation_method.py.jinja')
        return template.render(
            method_name=method_name,
            params=params,
            return_type=return_type,
            docstring=docstring,
            body_lines=body_lines
        )

    def _map_param_type(self, schema_type: str) -> str:
        """Map parameter schema type to Python type."""
        type_map = {
            "string": "str",
            "integer": "int",
            "number": "float",
            "boolean": "bool",
            "array": "list[Any]",
        }
        return type_map.get(schema_type, "Any")

    # ===== Package Init =====

    def _generate_init_file(self) -> GeneratedFile:
        """Generate __init__.py with exports."""
        template = self.jinja_env.get_template('python/__init__.py.jinja')
        content = template.render(
            has_enums=bool(self.get_enum_schemas())
        )

        return GeneratedFile(
            path="__init__.py",
            content=content,
            description="Package exports",
        )

    # ===== Per-App Folder Generation (Namespaced Structure) =====

    def _generate_app_folder(self, tag: str, operations: list[IROperationObject]) -> list[GeneratedFile]:
        """Generate folder for a specific app (tag)."""
        files = []

        # Get schemas used by this app
        app_schemas = self._get_schemas_for_operations(operations)

        # Generate models.py for this app
        files.append(self._generate_app_models_file(tag, app_schemas, operations))

        # Generate client.py for this app
        files.append(self._generate_app_client_file(tag, operations))

        # Generate __init__.py for this app
        files.append(self._generate_app_init_file(tag, operations))

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

    def _generate_app_models_file(self, tag: str, schemas: dict[str, IRSchemaObject], operations: list[IROperationObject]) -> GeneratedFile:
        """Generate models.py for a specific app."""
        # Check if we have enums in schemas
        app_enums = self._collect_enums_from_schemas(schemas)
        has_enums = len(app_enums) > 0

        # Generate schemas
        schema_codes = []
        for name, schema in schemas.items():
            schema_codes.append(self.generate_schema(schema))

        template = self.jinja_env.get_template('python/models/app_models.py.jinja')
        content = template.render(
            has_enums=has_enums,
            enum_names=sorted(app_enums.keys()) if has_enums else [],
            schemas=schema_codes if schema_codes else ["pass"]
        )

        folder_name = self.tag_and_app_to_folder_name(tag, operations)
        return GeneratedFile(
            path=f"{folder_name}/models.py",
            content=content,
            description=f"Pydantic models for {tag}",
        )

    def _generate_app_client_file(self, tag: str, operations: list[IROperationObject]) -> GeneratedFile:
        """Generate client.py for a specific app."""
        class_name = self.tag_to_class_name(tag)

        # Generate methods
        method_codes = []
        for operation in operations:
            method_codes.append(self.generate_operation(operation, remove_tag_prefix=True))

        template = self.jinja_env.get_template('python/client/app_client.py.jinja')
        content = template.render(
            tag=self.tag_to_display_name(tag),
            class_name=class_name,
            operations=method_codes
        )

        folder_name = self.tag_and_app_to_folder_name(tag, operations)
        return GeneratedFile(
            path=f"{folder_name}/client.py",
            content=content,
            description=f"API client for {tag}",
        )

    def _generate_app_init_file(self, tag: str, operations: list[IROperationObject]) -> GeneratedFile:
        """Generate __init__.py for a specific app."""
        class_name = self.tag_to_class_name(tag)

        template = self.jinja_env.get_template('python/app_init.py.jinja')
        content = template.render(class_name=class_name)

        folder_name = self.tag_and_app_to_folder_name(tag, operations)
        return GeneratedFile(
            path=f"{folder_name}/__init__.py",
            content=content,
            description=f"Package exports for {tag}",
        )

    def _generate_main_client_file(self, ops_by_tag: dict) -> GeneratedFile:
        """Generate main client.py with APIClient."""
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

        template = self.jinja_env.get_template('python/client/main_client_file.py.jinja')
        content = template.render(
            tags=tags_data,
            client_code=client_code
        )

        return GeneratedFile(
            path="client.py",
            content=content,
            description="Main API client",
        )

    def _generate_main_init_file(self) -> GeneratedFile:
        """Generate main __init__.py with API class and JWT management."""
        ops_by_tag = self.group_operations_by_tag()
        tags = sorted(ops_by_tag.keys())

        # Prepare tags data for template
        tags_data = [
            {
                "class_name": self.tag_to_class_name(tag),
                "slug": self.tag_and_app_to_folder_name(tag, ops_by_tag[tag]),
            }
            for tag in tags
        ]

        # Check if we have enums
        all_schemas = self.context.schemas
        all_enums = self._collect_enums_from_schemas(all_schemas)

        # API class
        api_class = self._generate_api_wrapper_class_python(tags)

        template = self.jinja_env.get_template('python/main_init.py.jinja')
        content = template.render(
            api_title=self.context.openapi_info.title,
            tags=tags_data,
            has_enums=bool(all_enums),
            enum_names=sorted(all_enums.keys()) if all_enums else [],
            api_class=api_class
        )

        return GeneratedFile(
            path="__init__.py",
            content=content,
            description="Package exports with API class and JWT management",
        )

    def _generate_api_wrapper_class_python(self, tags: list[str]) -> str:
        """Generate API wrapper class with JWT management for Python."""
        # Prepare property data
        properties_data = []
        for tag in tags:
            properties_data.append({
                "tag": tag,
                "class_name": self.tag_to_class_name(tag),
                "property": self.tag_to_property_name(tag),
            })

        template = self.jinja_env.get_template('python/api_wrapper.py.jinja')
        return template.render(properties=properties_data)

    def _generate_logger_file(self) -> GeneratedFile:
        """Generate logger.py with Rich integration."""
        template = self.jinja_env.get_template('python/utils/logger.py.jinja')
        content = template.render()

        return GeneratedFile(
            path="logger.py",
            content=content,
            description="API Logger with Rich",
        )

    def _generate_schema_file(self) -> GeneratedFile:
        """Generate schema.py with OpenAPI schema as dict."""
        import json
        import re

        # First, convert to pretty JSON
        schema_json = json.dumps(self.openapi_schema, indent=4, ensure_ascii=False)

        # Convert JSON literals to Python literals
        schema_json = re.sub(r'\btrue\b', 'True', schema_json)
        schema_json = re.sub(r'\bfalse\b', 'False', schema_json)
        schema_json = re.sub(r'\bnull\b', 'None', schema_json)

        template = self.jinja_env.get_template('python/utils/schema.py.jinja')
        content = template.render(schema_dict=schema_json)

        return GeneratedFile(
            path="schema.py",
            content=content,
            description="OpenAPI Schema",
        )
