"""
SWR Hooks Generator - Generates React hooks for data fetching.

This generator creates SWR-based React hooks from IR:
- Query hooks (GET operations) using useSWR
- Mutation hooks (POST/PUT/PATCH/DELETE) using useSWRConfig
- Automatic key generation
- Type-safe parameters and responses
- Optimistic updates support

Architecture:
    - Query hooks: useSWR with automatic key management
    - Mutation hooks: Custom hooks with revalidation
    - Works only in React client components
"""

from __future__ import annotations

from jinja2 import Environment

from ...ir import IRContext, IROperationObject
from ..base import BaseGenerator, GeneratedFile
from .naming import operation_to_method_name


class HooksGenerator:
    """
    SWR hooks generator for React.

    Generates:
    - useResource() hooks for GET operations
    - useCreateResource() hooks for POST
    - useUpdateResource() hooks for PUT/PATCH
    - useDeleteResource() hooks for DELETE
    """

    def __init__(self, jinja_env: Environment, context: IRContext, base: BaseGenerator):
        self.jinja_env = jinja_env
        self.context = context
        self.base = base

    def generate_query_hook(self, operation: IROperationObject) -> str:
        """
        Generate useSWR hook for GET operation using Jinja2 template.

        Examples:
            >>> generate_query_hook(users_list)
            export function useShopProducts(params?: { page?: number }) {
              return useSWR(
                params ? ['shop-products', params] : 'shop-products',
                () => Fetchers.getShopProducts(params)
              )
            }
        """
        # Get hook name
        hook_name = self._operation_to_hook_name(operation)

        # Get fetcher function name
        fetcher_name = self._operation_to_fetcher_name(operation)

        # Get parameters
        param_info = self._get_param_info(operation)

        # Get response type
        response_type = self._get_response_type(operation)

        # Get SWR key
        swr_key = self._generate_swr_key(operation)

        # Render template
        template = self.jinja_env.get_template('hooks/query_hook.ts.jinja')
        return template.render(
            operation=operation,
            hook_name=hook_name,
            fetcher_name=fetcher_name,
            func_params=param_info['func_params'],
            fetcher_params=param_info['fetcher_params'],
            response_type=response_type,
            swr_key=swr_key
        )

    def generate_mutation_hook(self, operation: IROperationObject) -> str:
        """
        Generate mutation hook for POST/PUT/PATCH/DELETE using Jinja2 template.

        Examples:
            >>> generate_mutation_hook(users_create)
            export function useCreateShopProduct() {
              const { mutate } = useSWRConfig()

              return async (data: ProductCreateRequest) => {
                const result = await Fetchers.createShopProduct(data)
                mutate('shop-products')
                return result
              }
            }
        """
        # Get hook name
        hook_name = self._operation_to_hook_name(operation)

        # Get fetcher function name
        fetcher_name = self._operation_to_fetcher_name(operation)

        # Get parameters
        param_info = self._get_param_info(operation)

        # Get response type
        response_type = self._get_response_type(operation)

        # Get revalidation keys
        revalidation_keys = self._get_revalidation_keys(operation)

        # Render template
        template = self.jinja_env.get_template('hooks/mutation_hook.ts.jinja')
        return template.render(
            operation=operation,
            hook_name=hook_name,
            fetcher_name=fetcher_name,
            func_params=param_info['func_params'],
            fetcher_params=param_info['fetcher_params'],
            response_type=response_type,
            revalidation_keys=revalidation_keys
        )

    def _operation_to_hook_name(self, operation: IROperationObject) -> str:
        """
        Convert operation to hook name.
        
        Hooks are organized into tag-specific files but also exported globally,
        so we include the tag in the name to avoid collisions.
        
        Examples:
            cfg_support_tickets_list -> useSupportTicketsList
            cfg_health_drf_retrieve -> useHealthDrf
            cfg_accounts_otp_request_create -> useCreateAccountsOtpRequest
        """

        # Remove cfg_ prefix but keep tag + resource for uniqueness (same as fetchers)
        operation_id = operation.operation_id
        if operation_id.startswith('django_cfg_'):
            operation_id = operation_id.replace('django_cfg_', '', 1)
        elif operation_id.startswith('cfg_'):
            operation_id = operation_id.replace('cfg_', '', 1)

        # Determine prefix based on HTTP method
        if operation.http_method == 'GET':
            prefix = 'use'
        elif operation.http_method == 'POST':
            prefix = 'useCreate'
        elif operation.http_method in ('PUT', 'PATCH'):
            if '_partial_update' in operation_id:
                prefix = 'usePartialUpdate'
            else:
                prefix = 'useUpdate'
        elif operation.http_method == 'DELETE':
            prefix = 'useDelete'
        else:
            prefix = 'use'

        # For hooks, path is not critical but pass for consistency
        return operation_to_method_name(operation_id, operation.http_method, prefix, self.base, operation.path)

    def _operation_to_fetcher_name(self, operation: IROperationObject) -> str:
        """Get corresponding fetcher function name (must match fetchers_generator logic)."""


        # Remove cfg_ prefix but keep tag + resource (must match fetchers_generator exactly)
        operation_id = operation.operation_id
        if operation_id.startswith('django_cfg_'):
            operation_id = operation_id.replace('django_cfg_', '', 1)
        elif operation_id.startswith('cfg_'):
            operation_id = operation_id.replace('cfg_', '', 1)

        # Determine prefix (must match fetchers_generator exactly)
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

        # Must match fetchers exactly, including path
        return operation_to_method_name(operation_id, operation.http_method, prefix, self.base, operation.path)

    def _get_param_info(self, operation: IROperationObject) -> dict:
        """
        Get parameter info for hook.

        Returns:
            {
                'func_params': Function parameters for hook signature
                'fetcher_params': Parameters to pass to fetcher
            }
        """
        func_params = []
        fetcher_params = []

        # Path parameters
        if operation.path_parameters:
            for param in operation.path_parameters:
                param_type = self._map_param_type(param.schema_type)
                func_params.append(f"{param.name}: {param_type}")
                fetcher_params.append(param.name)

        # Request body (must come BEFORE query params to match fetcher signature!)
        if operation.request_body:
            schema_name = operation.request_body.schema_name
            # Use schema only if it exists as a component (not inline)
            if schema_name and schema_name in self.context.schemas:
                body_type = schema_name
            else:
                body_type = "any"
            func_params.append(f"data: {body_type}")
            fetcher_params.append("data")
        elif operation.patch_request_body:
            # PATCH request body (optional)
            schema_name = operation.patch_request_body.schema_name
            if schema_name and schema_name in self.context.schemas:
                func_params.append(f"data?: {schema_name}")
                fetcher_params.append("data")
            else:
                func_params.append("data?: any")
                fetcher_params.append("data")

        # Query parameters (must come AFTER request body to match fetcher signature!)
        if operation.query_parameters:
            query_fields = []
            # Check if any query param is required (not all!)
            # TypeScript doesn't allow required fields in optional objects
            has_required = any(param.required for param in operation.query_parameters)

            for param in operation.query_parameters:
                param_type = self._map_param_type(param.schema_type)
                optional = "?" if not param.required else ""
                query_fields.append(f"{param.name}{optional}: {param_type}")

            if query_fields:
                params_optional = "" if has_required else "?"
                func_params.append(f"params{params_optional}: {{ {'; '.join(query_fields)} }}")
                fetcher_params.append("params")

        return {
            'func_params': ", ".join(func_params) if func_params else "",
            'fetcher_params': ", ".join(fetcher_params) if fetcher_params else ""
        }

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

    def _get_response_type(self, operation: IROperationObject) -> str:
        """Get response type for hook."""
        # Get 2xx response
        for status_code in [200, 201, 202, 204]:
            if status_code in operation.responses:
                response = operation.responses[status_code]
                if response.schema_name:
                    return response.schema_name

        # No response or void
        if 204 in operation.responses or operation.http_method == "DELETE":
            return "void"

        return "any"

    def _generate_swr_key(self, operation: IROperationObject) -> str:
        """
        Generate SWR key for query.

        Examples:
            GET /products/ -> 'shop-products'
            GET /products/{id}/ -> ['shop-product', id]
            GET /products/?category=5 -> ['shop-products', params]
        """
        # Get resource name from operation_id
        op_id = operation.operation_id

        # Determine if list or detail
        is_list = op_id.endswith("_list")
        is_detail = op_id.endswith("_retrieve")

        # Remove common suffixes
        resource = op_id.replace("_list", "").replace("_retrieve", "")

        # For detail views, use singular form
        if is_detail:
            resource = resource.rstrip('s') if resource.endswith('s') and len(resource) > 1 else resource

        # Convert to kebab-case
        key_base = resource.replace("_", "-")

        # Check if has path params or query params
        has_path_params = bool(operation.path_parameters)
        has_query_params = bool(operation.query_parameters)

        if has_path_params:
            # Single resource: ['shop-product', id]
            param_name = operation.path_parameters[0].name
            return f"['{key_base}', {param_name}]"
        elif has_query_params:
            # List with params: params ? ['shop-products', params] : 'shop-products'
            return f"params ? ['{key_base}', params] : '{key_base}'"
        else:
            # Simple key: 'shop-products'
            return f"'{key_base}'"

    def _get_revalidation_keys(self, operation: IROperationObject) -> list[str]:
        """
        Get SWR keys that should be revalidated after mutation.

        Examples:
            POST /products/ -> ['shop-products']
            PUT /products/{id}/ -> ['shop-products', 'shop-product']
            DELETE /products/{id}/ -> ['shop-products']
        """
        keys = []

        op_id = operation.operation_id
        resource = op_id.replace("_create", "").replace("_update", "").replace("_partial_update", "").replace("_destroy", "")

        # List key (for revalidating lists)
        list_key = f"{resource.replace('_', '-')}"
        keys.append(list_key)

        # Detail key (for update/delete operations)
        if operation.http_method in ("PUT", "PATCH", "DELETE"):
            detail_key = f"{resource.replace('_', '-').rstrip('s')}"
            if detail_key != list_key:
                keys.append(detail_key)

        return keys

    def generate_tag_hooks_file(
        self,
        tag: str,
        operations: list[IROperationObject],
    ) -> GeneratedFile:
        """
        Generate hooks file for a specific tag/resource using Jinja2 template.

        Args:
            tag: Tag name (e.g., "shop_products")
            operations: List of operations for this tag

        Returns:
            GeneratedFile with hooks
        """
        # Separate queries and mutations & collect schema names
        hooks = []
        schema_names = set()
        has_queries = False
        has_mutations = False

        for operation in operations:
            # Collect schemas used in this operation (only if they exist as components)
            if operation.request_body and operation.request_body.schema_name:
                if operation.request_body.schema_name in self.context.schemas:
                    schema_names.add(operation.request_body.schema_name)
            if operation.patch_request_body and operation.patch_request_body.schema_name:
                if operation.patch_request_body.schema_name in self.context.schemas:
                    schema_names.add(operation.patch_request_body.schema_name)

            # Get response schema
            response = operation.primary_success_response
            if response and response.schema_name:
                schema_names.add(response.schema_name)

            # Generate hook and track operation types
            if operation.http_method == "GET":
                hooks.append(self.generate_query_hook(operation))
                has_queries = True
            else:
                hooks.append(self.generate_mutation_hook(operation))
                has_mutations = True

        # Get display name for documentation
        tag_display_name = self.base.tag_to_display_name(tag)

        # Get tag file name for fetchers import
        folder_name = self.base.tag_and_app_to_folder_name(tag, operations)
        tag_file = folder_name

        # Render template
        template = self.jinja_env.get_template('hooks/hooks.ts.jinja')
        content = template.render(
            tag_display_name=tag_display_name,
            tag_file=tag_file,
            has_schemas=bool(schema_names),
            schema_names=sorted(schema_names),
            has_queries=has_queries,
            has_mutations=has_mutations,
            hooks=hooks
        )

        # Get file path (use same naming as APIClient)
        file_path = f"_utils/hooks/{folder_name}.ts"

        return GeneratedFile(
            path=file_path,
            content=content,
            description=f"SWR hooks for {tag_display_name}",
        )

    def generate_hooks_index_file(self, module_names: list[str]) -> GeneratedFile:
        """Generate index.ts for hooks folder using Jinja2 template."""
        template = self.jinja_env.get_template('hooks/index.ts.jinja')
        content = template.render(modules=module_names)

        return GeneratedFile(
            path="_utils/hooks/index.ts",
            content=content,
            description="Index file for SWR hooks",
        )
