"""
Fetchers Generator - Generates typed fetcher functions from IR.

This generator creates universal TypeScript functions that:
- Use Zod schemas for runtime validation
- Work in any environment (Next.js, React Native, Node.js)
- Are type-safe with proper TypeScript types
- Can be used with any data-fetching library
"""

from __future__ import annotations

from jinja2 import Environment
from ..base import GeneratedFile, BaseGenerator
from ...ir import IRContext, IROperationObject


class FetchersGenerator:
    """
    Generate typed fetcher functions from IR operations.

    Features:
    - Runtime validation with Zod
    - Type-safe parameters and responses
    - Works with any data-fetching library (SWR, React Query)
    - Server Component compatible
    """

    def __init__(self, jinja_env: Environment, context: IRContext, base: BaseGenerator):
        self.jinja_env = jinja_env
        self.context = context
        self.base = base

    def generate_fetcher_function(self, operation: IROperationObject) -> str:
        """
        Generate a single fetcher function for an operation.

        Args:
            operation: IROperationObject to convert to fetcher

        Returns:
            TypeScript fetcher function code

        Examples:
            >>> generate_fetcher_function(users_list)
            export async function getUsers(params?: GetUsersParams): Promise<PaginatedUser> {
              const response = await api.users.list(params)
              return PaginatedUserSchema.parse(response)
            }
        """
        # Get function name (e.g., "getUsers", "createUser")
        func_name = self._operation_to_function_name(operation)

        # Get parameters structure
        param_info = self._get_param_structure(operation)

        # Get response type and schema
        response_type, response_schema = self._get_response_info(operation)

        # Get API client call
        api_call = self._get_api_call(operation)

        # Build JSDoc comment
        jsdoc = self._generate_jsdoc(operation, func_name)

        # Build function
        lines = []

        # JSDoc
        if jsdoc:
            lines.append(jsdoc)

        # Function signature with optional client parameter
        if param_info['func_params']:
            lines.append(f"export async function {func_name}(")
            lines.append(f"  {param_info['func_params']},")
            lines.append(f"  client?: API")
            lines.append(f"): Promise<{response_type}> {{")
        else:
            lines.append(f"export async function {func_name}(")
            lines.append(f"  client?: API")
            lines.append(f"): Promise<{response_type}> {{")

        # Get client instance (either passed or global)
        lines.append("  const api = client || getAPIInstance()")
        lines.append("")

        # Function body - build API call
        api_call_params = param_info['api_call_params']
        # Replace API. with api.
        api_call_instance = api_call.replace("API.", "api.")

        if api_call_params:
            lines.append(f"  const response = await {api_call_instance}({api_call_params})")
        else:
            lines.append(f"  const response = await {api_call_instance}()")

        # Validation with Zod
        if response_schema:
            lines.append(f"  return {response_schema}.parse(response)")
        else:
            lines.append("  return response")

        lines.append("}")

        return "\n".join(lines)

    def _operation_to_function_name(self, operation: IROperationObject) -> str:
        """
        Convert operation to function name.

        Examples:
            users_list (GET) -> getUsersList
            users_retrieve (GET) -> getUsersById
            users_create (POST) -> createUsers
            users_update (PUT) -> updateUsers
            users_partial_update (PATCH) -> partialUpdateUsers
            users_destroy (DELETE) -> deleteUsers
        """
        # Remove tag prefix from operation_id
        op_id = operation.operation_id

        # Handle common patterns - keep full resource name for uniqueness
        if op_id.endswith("_list"):
            resource = op_id.removesuffix("_list")
            return f"get{self._to_pascal_case(resource)}List"
        elif op_id.endswith("_retrieve"):
            resource = op_id.removesuffix("_retrieve")
            # Add ById suffix to distinguish from list
            return f"get{self._to_pascal_case(resource)}ById"
        elif op_id.endswith("_create"):
            resource = op_id.removesuffix("_create")
            return f"create{self._to_pascal_case(resource)}"
        elif op_id.endswith("_partial_update"):
            resource = op_id.removesuffix("_partial_update")
            return f"partialUpdate{self._to_pascal_case(resource)}"
        elif op_id.endswith("_update"):
            resource = op_id.removesuffix("_update")
            return f"update{self._to_pascal_case(resource)}"
        elif op_id.endswith("_destroy"):
            resource = op_id.removesuffix("_destroy")
            return f"delete{self._to_pascal_case(resource)}"
        else:
            # Custom action - use operation_id as is
            return self._to_camel_case(op_id)

    def _to_pascal_case(self, snake_str: str) -> str:
        """Convert snake_case to PascalCase."""
        return ''.join(word.capitalize() for word in snake_str.split('_'))

    def _to_camel_case(self, snake_str: str) -> str:
        """Convert snake_case to camelCase."""
        components = snake_str.split('_')
        return components[0] + ''.join(x.capitalize() for x in components[1:])

    def _get_param_structure(self, operation: IROperationObject) -> dict:
        """
        Get structured parameter information for function generation.

        Returns dict with:
            - func_params: Function signature params (e.g., "slug: string, params?: { page?: number }")
            - api_call_params: API call params (e.g., "slug, params" or "slug" or "params")

        Examples:
            GET /users/{id}/ -> {
                func_params: "id: number",
                api_call_params: "id"
            }

            GET /users/ with query params -> {
                func_params: "params?: { page?: number }",
                api_call_params: "params"
            }

            GET /users/{id}/ with query params -> {
                func_params: "id: number, params?: { page?: number }",
                api_call_params: "id, params"
            }

            POST /users/ -> {
                func_params: "data: UserRequest",
                api_call_params: "data"
            }

            POST /users/{id}/action/ -> {
                func_params: "id: number, data: ActionRequest",
                api_call_params: "id, data"
            }
        """
        func_params = []
        api_call_params = []

        # Path parameters (always passed individually)
        if operation.path_parameters:
            for param in operation.path_parameters:
                param_type = self._map_param_type(param.schema_type)
                func_params.append(f"{param.name}: {param_type}")
                api_call_params.append(param.name)

        # Query parameters (passed as params object, but unpacked when calling API)
        if operation.query_parameters:
            query_fields = []
            # params is required only if all parameters are required
            all_required = all(param.required for param in operation.query_parameters)
            params_accessor = "params." if all_required else "params?."

            for param in operation.query_parameters:
                param_type = self._map_param_type(param.schema_type)
                optional = "?" if not param.required else ""
                query_fields.append(f"{param.name}{optional}: {param_type}")
                # Unpack from params object when calling API
                api_call_params.append(f"{params_accessor}{param.name}")

            if query_fields:
                params_optional = "" if all_required else "?"
                func_params.append(f"params{params_optional}: {{ {'; '.join(query_fields)} }}")

        # Request body (passed as data)
        if operation.request_body:
            schema_name = operation.request_body.schema_name
            # Use schema only if it exists as a component (not inline)
            if schema_name and schema_name in self.context.schemas:
                body_type = schema_name
            else:
                body_type = "any"
            func_params.append(f"data: {body_type}")
            api_call_params.append("data")

        return {
            'func_params': ", ".join(func_params) if func_params else "",
            'api_call_params': ", ".join(api_call_params) if api_call_params else ""
        }

    def _get_params_type(self, operation: IROperationObject) -> tuple[str, bool]:
        """
        Get parameters type definition.

        Returns:
            (type_definition, has_params)

        Examples:
            ("params?: { page?: number; page_size?: number }", True)
            ("id: number", True)
            ("", False)
        """
        params = []

        # Path parameters
        if operation.path_parameters:
            for param in operation.path_parameters:
                param_type = self._map_param_type(param.schema_type)
                params.append(f"{param.name}: {param_type}")

        # Query parameters
        if operation.query_parameters:
            query_fields = []
            all_required = all(param.required for param in operation.query_parameters)

            for param in operation.query_parameters:
                param_type = self._map_param_type(param.schema_type)
                optional = "?" if not param.required else ""
                query_fields.append(f"{param.name}{optional}: {param_type}")

            if query_fields:
                params_optional = "" if all_required else "?"
                params.append(f"params{params_optional}: {{ {'; '.join(query_fields)} }}")

        # Request body
        if operation.request_body:
            schema_name = operation.request_body.schema_name
            # Use schema only if it exists as a component (not inline)
            if schema_name and schema_name in self.context.schemas:
                body_type = schema_name
            else:
                body_type = "any"
            params.append(f"data: {body_type}")

        if not params:
            return ("", False)

        return (", ".join(params), True)

    def _map_param_type(self, param_type: str) -> str:
        """Map OpenAPI param type to TypeScript type."""
        type_map = {
            "integer": "number",
            "number": "number",
            "string": "string",
            "boolean": "boolean",
            "array": "any[]",
            "object": "any",
        }
        return type_map.get(param_type, "any")

    def _get_response_info(self, operation: IROperationObject) -> tuple[str, str | None]:
        """
        Get response type and schema name.

        Returns:
            (response_type, response_schema_name)

        Examples:
            ("PaginatedUser", "PaginatedUserSchema")
            ("User", "UserSchema")
            ("void", None)
        """
        # Get 2xx response
        for status_code in [200, 201, 202, 204]:
            if status_code in operation.responses:
                response = operation.responses[status_code]
                if response.schema_name:
                    schema_name = response.schema_name
                    return (schema_name, f"{schema_name}Schema")

        # No response or void
        if 204 in operation.responses or operation.http_method == "DELETE":
            return ("void", None)

        return ("any", None)

    def _get_api_call(self, operation: IROperationObject) -> str:
        """
        Get API client method call path.

        Examples:
            API.users.list
            API.users.retrieve
            API.posts.create
        """
        # Get tag/resource name
        tag = operation.tags[0] if operation.tags else "default"
        tag_property = self.base.tag_to_property_name(tag)

        # Get method name from operation_id
        method_name = self.base.remove_tag_prefix(operation.operation_id, tag)
        method_name = self._to_camel_case(method_name)

        return f"API.{tag_property}.{method_name}"

    def _generate_jsdoc(self, operation: IROperationObject, func_name: str) -> str:
        """Generate JSDoc comment for function."""
        lines = ["/**"]

        # Summary
        if operation.summary:
            lines.append(f" * {operation.summary}")
        else:
            lines.append(f" * {func_name}")

        # Description
        if operation.description:
            lines.append(" *")
            for desc_line in operation.description.split("\n"):
                lines.append(f" * {desc_line}")

        # HTTP method and path
        lines.append(" *")
        lines.append(f" * @method {operation.http_method}")
        lines.append(f" * @path {operation.path}")

        lines.append(" */")
        return "\n".join(lines)

    def generate_tag_fetchers_file(
        self,
        tag: str,
        operations: list[IROperationObject],
    ) -> GeneratedFile:
        """
        Generate fetchers file for a specific tag/resource.

        Args:
            tag: Tag name (e.g., "users", "posts")
            operations: List of operations for this tag

        Returns:
            GeneratedFile with fetchers
        """
        # Generate individual fetchers
        fetchers = []
        schema_names = set()

        for operation in operations:
            fetcher_code = self.generate_fetcher_function(operation)
            fetchers.append(fetcher_code)

            # Collect schema names
            _, response_schema = self._get_response_info(operation)
            if response_schema:
                schema_name = response_schema.replace("Schema", "")
                schema_names.add(schema_name)

            # Add request body schemas (only if they exist as components)
            if operation.request_body and operation.request_body.schema_name:
                # Only add if schema exists in components (not inline)
                if operation.request_body.schema_name in self.context.schemas:
                    schema_names.add(operation.request_body.schema_name)

        # Get display name and folder name (use same naming as APIClient)
        tag_display_name = self.base.tag_to_display_name(tag)
        folder_name = self.base.tag_and_app_to_folder_name(tag, operations)

        # Render template
        template = self.jinja_env.get_template("fetchers/fetchers.ts.jinja")
        content = template.render(
            tag_display_name=tag_display_name,
            fetchers=fetchers,
            has_schemas=bool(schema_names),
            schema_names=sorted(schema_names),
            has_client=True,
        )

        return GeneratedFile(
            path=f"_utils/fetchers/{folder_name}.ts",
            content=content,
            description=f"Typed fetchers for {tag_display_name}",
        )

    def generate_fetchers_index_file(self, module_names: list[str]) -> GeneratedFile:
        """Generate index.ts for fetchers folder."""
        template = self.jinja_env.get_template("fetchers/index.ts.jinja")
        content = template.render(modules=sorted(module_names))

        return GeneratedFile(
            path="_utils/fetchers/index.ts",
            content=content,
            description="Fetchers index",
        )
