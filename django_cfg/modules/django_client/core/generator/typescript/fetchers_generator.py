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

from ...ir import IRContext, IROperationObject
from ..base import BaseGenerator, GeneratedFile
from .naming import operation_to_method_name
from .params_builder import ParamsBuilder


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
        self.params_builder = ParamsBuilder(context)

    def generate_fetcher_function(self, operation: IROperationObject) -> str:
        """
        Generate a single fetcher function for an operation using Jinja2 template.

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

        # Get parameters structure using universal builder
        params_structure = self.params_builder.build_params_structure(
            operation,
            for_fetcher=True
        )

        # Get response type and schema
        response_type, response_schema = self._get_response_info(operation)

        # Get API client call
        api_call = self._get_api_call(operation)
        # Replace API. with api. for instance method
        api_call_instance = api_call.replace("API.", "api.")

        # Render template
        template = self.jinja_env.get_template('fetchers/function.ts.jinja')
        return template.render(
            operation=operation,
            func_name=func_name,
            func_params=params_structure.func_signature,
            response_type=response_type,
            response_schema=response_schema,
            api_call=api_call_instance,
            api_call_params=params_structure.api_call_args
        )

    def _operation_to_function_name(self, operation: IROperationObject) -> str:
        """
        Convert operation to function name.
        
        Fetchers are organized into tag-specific files but also exported globally,
        so we include the tag in the name to avoid collisions.
        
        Examples:
            cfg_support_tickets_list -> getSupportTicketsList
            cfg_health_drf_retrieve -> getHealthDrf
            cfg_accounts_otp_request_create -> createAccountsOtpRequest
            cfg_accounts_profile_partial_update (PUT) -> partialUpdateAccountsProfilePut
        """


        # Remove cfg_ prefix but keep tag + resource for uniqueness
        operation_id = operation.operation_id
        # Remove only cfg_/django_cfg_ prefix
        if operation_id.startswith('django_cfg_'):
            operation_id = operation_id.replace('django_cfg_', '', 1)
        elif operation_id.startswith('cfg_'):
            operation_id = operation_id.replace('cfg_', '', 1)

        # Determine prefix based on HTTP method
        if operation.http_method == 'GET':
            prefix = 'get'
        elif operation.http_method == 'POST':
            prefix = 'create'
        elif operation.http_method in ('PUT', 'PATCH'):
            if '_partial_update' in operation_id:
                prefix = 'partialUpdate'
            else:
                prefix = 'update'
        elif operation.http_method == 'DELETE':
            prefix = 'delete'
        else:
            prefix = ''

        return operation_to_method_name(operation_id, operation.http_method, prefix, self.base)

    # REMOVED: _get_param_structure - replaced by ParamsBuilder

    # REMOVED: _get_params_type - replaced by ParamsBuilder
    # REMOVED: _map_param_type - moved to ParamsBuilder

    def _get_response_info(self, operation: IROperationObject) -> tuple[str, str | None]:
        """
        Get response type and schema name.

        Returns:
            (response_type, response_schema_name)

        Examples:
            ("PaginatedUser", "PaginatedUserSchema")
            ("User", "UserSchema")
            ("BotConfigSchema", "BotConfigSchemaSchema")  # handles names ending with "Schema"
            ("void", None)
        """
        # Get 2xx response
        for status_code in [200, 201, 202, 204]:
            if status_code in operation.responses:
                response = operation.responses[status_code]
                if response.schema_name:
                    schema_name = response.schema_name
                    # Always add "Schema" suffix for Zod schema name
                    # The schema generator always adds "Schema" suffix to create the constant name
                    # e.g., "Bot" -> "BotSchema", "BotConfigSchema" -> "BotConfigSchemaSchema"
                    return (schema_name, f"{schema_name}Schema")

        # No response or void
        if 204 in operation.responses or operation.http_method == "DELETE":
            return ("void", None)

        return ("any", None)

    def _get_api_call(self, operation: IROperationObject) -> str:
        """
        Get API client method call path.
        
        Must match the naming logic in operations_generator to ensure correct method calls.

        Examples:
            API.users.list
            API.users.retrieve
            API.posts.create
            API.accounts.otpRequest (custom action)
        """


        tag = operation.tags[0] if operation.tags else "default"
        tag_property = self.base.tag_to_property_name(tag)

        # Get method name using same logic as client generation (empty prefix)
        operation_id = self.base.remove_tag_prefix(operation.operation_id, tag)
        # Pass path to distinguish custom actions
        method_name = operation_to_method_name(operation_id, operation.http_method, '', self.base, operation.path)

        return f"API.{tag_property}.{method_name}"

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
                # response_schema has "Schema" suffix added (e.g., "BotConfigSchemaSchema")
                # Remove the last "Schema" suffix to get the original name (e.g., "BotConfigSchema")
                # This is used in the import template: import { {{ schema_name }}Schema, ... }
                if response_schema.endswith("Schema"):
                    schema_name = response_schema[:-6]  # Remove last 6 chars ("Schema")
                else:
                    schema_name = response_schema
                schema_names.add(schema_name)

            # Add request body schemas (only if they exist as components)
            if operation.request_body and operation.request_body.schema_name:
                # Only add if schema exists in components (not inline)
                if operation.request_body.schema_name in self.context.schemas:
                    schema_names.add(operation.request_body.schema_name)

            # Add patch request body schemas
            if operation.patch_request_body and operation.patch_request_body.schema_name:
                # Only add if schema exists in components (not inline)
                if operation.patch_request_body.schema_name in self.context.schemas:
                    schema_names.add(operation.patch_request_body.schema_name)

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
