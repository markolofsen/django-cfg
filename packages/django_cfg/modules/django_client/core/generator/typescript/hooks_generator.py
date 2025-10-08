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
from ..base import BaseGenerator, GeneratedFile
from ...ir import IROperationObject, IRContext


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
        Generate useSWR hook for GET operation.

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

        # Build hook
        lines = []

        # JSDoc
        lines.append("/**")
        if operation.summary:
            lines.append(f" * {operation.summary}")
        lines.append(" *")
        lines.append(f" * @method {operation.http_method}")
        lines.append(f" * @path {operation.path}")
        lines.append(" */")

        # Hook signature
        if param_info['func_params']:
            lines.append(f"export function {hook_name}({param_info['func_params']}) {{")
        else:
            lines.append(f"export function {hook_name}() {{")

        # useSWR call
        fetcher_params = param_info['fetcher_params']
        if fetcher_params:
            lines.append(f"  return useSWR<{response_type}>(")
            lines.append(f"    {swr_key},")
            lines.append(f"    () => Fetchers.{fetcher_name}({fetcher_params})")
            lines.append("  )")
        else:
            lines.append(f"  return useSWR<{response_type}>(")
            lines.append(f"    {swr_key},")
            lines.append(f"    () => Fetchers.{fetcher_name}()")
            lines.append("  )")

        lines.append("}")

        return "\n".join(lines)

    def generate_mutation_hook(self, operation: IROperationObject) -> str:
        """
        Generate mutation hook for POST/PUT/PATCH/DELETE.

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

        # Build hook
        lines = []

        # JSDoc
        lines.append("/**")
        if operation.summary:
            lines.append(f" * {operation.summary}")
        lines.append(" *")
        lines.append(f" * @method {operation.http_method}")
        lines.append(f" * @path {operation.path}")
        lines.append(" */")

        # Hook signature
        lines.append(f"export function {hook_name}() {{")
        lines.append("  const { mutate } = useSWRConfig()")
        lines.append("")

        # Return async function
        if param_info['func_params']:
            lines.append(f"  return async ({param_info['func_params']}): Promise<{response_type}> => {{")
        else:
            lines.append(f"  return async (): Promise<{response_type}> => {{")

        # Call fetcher
        fetcher_params = param_info['fetcher_params']
        if fetcher_params:
            lines.append(f"    const result = await Fetchers.{fetcher_name}({fetcher_params})")
        else:
            lines.append(f"    const result = await Fetchers.{fetcher_name}()")

        # Revalidate
        if revalidation_keys:
            lines.append("")
            lines.append("    // Revalidate related queries")
            for key in revalidation_keys:
                lines.append(f"    mutate('{key}')")

        lines.append("")
        lines.append("    return result")
        lines.append("  }")
        lines.append("}")

        return "\n".join(lines)

    def _operation_to_hook_name(self, operation: IROperationObject) -> str:
        """
        Convert operation to hook name.

        Examples:
            users_list (GET) -> useUsers
            users_retrieve (GET) -> useUser
            users_create (POST) -> useCreateUser
            users_update (PUT) -> useUpdateUser
            users_partial_update (PATCH) -> useUpdateUser
            users_destroy (DELETE) -> useDeleteUser
        """
        op_id = operation.operation_id

        if op_id.endswith("_list"):
            resource = op_id.replace("_list", "")
            # Plural form
            return f"use{self._to_pascal_case(resource)}"
        elif op_id.endswith("_retrieve"):
            resource = op_id.replace("_retrieve", "")
            # Singular form (remove trailing 's')
            resource_singular = resource.rstrip('s') if resource.endswith('s') and len(resource) > 1 else resource
            return f"use{self._to_pascal_case(resource_singular)}"
        elif op_id.endswith("_create"):
            resource = op_id.removesuffix("_create")
            return f"useCreate{self._to_pascal_case(resource)}"
        elif op_id.endswith("_partial_update"):
            resource = op_id.removesuffix("_partial_update")
            return f"usePartialUpdate{self._to_pascal_case(resource)}"
        elif op_id.endswith("_update"):
            resource = op_id.removesuffix("_update")
            return f"useUpdate{self._to_pascal_case(resource)}"
        elif op_id.endswith("_destroy"):
            resource = op_id.removesuffix("_destroy")
            return f"useDelete{self._to_pascal_case(resource)}"
        else:
            # Custom action
            return f"use{self._to_pascal_case(op_id)}"

    def _operation_to_fetcher_name(self, operation: IROperationObject) -> str:
        """Get corresponding fetcher function name."""
        op_id = operation.operation_id

        # Remove only suffix, not all occurrences (same logic as fetchers_generator)
        if op_id.endswith("_list"):
            resource = op_id.removesuffix("_list")
            return f"get{self._to_pascal_case(resource)}"
        elif op_id.endswith("_retrieve"):
            resource = op_id.removesuffix("_retrieve")
            # Singular
            resource_singular = resource.rstrip('s') if resource.endswith('s') else resource
            return f"get{self._to_pascal_case(resource_singular)}"
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
            return f"{operation.http_method.lower()}{self._to_pascal_case(op_id)}"

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
                func_params.append(f"params{params_optional}: {{ {'; '.join(query_fields)} }}")
                fetcher_params.append("params")

        # Request body
        if operation.request_body:
            schema_name = operation.request_body.schema_name
            # Use schema only if it exists as a component (not inline)
            if schema_name and schema_name in self.context.schemas:
                body_type = schema_name
            else:
                body_type = "any"
            func_params.append(f"data: {body_type}")
            fetcher_params.append("data")

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

    def _to_pascal_case(self, snake_str: str) -> str:
        """Convert snake_case to PascalCase."""
        return ''.join(word.capitalize() for word in snake_str.split('_'))

    def generate_tag_hooks_file(
        self,
        tag: str,
        operations: list[IROperationObject],
    ) -> GeneratedFile:
        """
        Generate hooks file for a specific tag/resource.

        Args:
            tag: Tag name (e.g., "shop_products")
            operations: List of operations for this tag

        Returns:
            GeneratedFile with hooks
        """
        # Separate queries and mutations & collect schema names
        query_hooks = []
        mutation_hooks = []
        schema_names = set()

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

            # Generate hook
            if operation.http_method == "GET":
                query_hooks.append(self.generate_query_hook(operation))
            else:
                mutation_hooks.append(self.generate_mutation_hook(operation))

        # Get display name for documentation
        tag_display_name = self.base.tag_to_display_name(tag)

        # Build file content
        lines = []

        # Header
        lines.append("/**")
        lines.append(f" * SWR Hooks for {tag_display_name}")
        lines.append(" *")
        lines.append(" * Auto-generated React hooks for data fetching with SWR.")
        lines.append(" *")
        lines.append(" * Setup:")
        lines.append(" * ```typescript")
        lines.append(" * // Configure API once (in your app root)")
        lines.append(" * import { configureAPI } from '../../api-instance'")
        lines.append(" * configureAPI({ baseUrl: 'https://api.example.com' })")
        lines.append(" * ```")
        lines.append(" *")
        lines.append(" * Usage:")
        lines.append(" * ```typescript")
        lines.append(" * // Query hook")
        lines.append(" * const { data, error, mutate } = useShopProducts({ page: 1 })")
        lines.append(" *")
        lines.append(" * // Mutation hook")
        lines.append(" * const createProduct = useCreateShopProduct()")
        lines.append(" * await createProduct({ name: 'Product', price: 99 })")
        lines.append(" * ```")
        lines.append(" */")

        # Import types from schemas
        for schema_name in sorted(schema_names):
            lines.append(f"import type {{ {schema_name} }} from '../schemas/{schema_name}.schema'")

        lines.append("import useSWR from 'swr'")
        lines.append("import { useSWRConfig } from 'swr'")
        lines.append("import * as Fetchers from '../fetchers'")
        lines.append("")

        # Query hooks
        if query_hooks:
            lines.append("// ===== Query Hooks (GET) =====")
            lines.append("")
            for hook in query_hooks:
                lines.append(hook)
                lines.append("")

        # Mutation hooks
        if mutation_hooks:
            lines.append("// ===== Mutation Hooks (POST/PUT/PATCH/DELETE) =====")
            lines.append("")
            for hook in mutation_hooks:
                lines.append(hook)
                lines.append("")

        content = "\n".join(lines)

        # Get file path (use same naming as APIClient)
        folder_name = self.base.tag_and_app_to_folder_name(tag, operations)
        file_path = f"_utils/hooks/{folder_name}.ts"

        return GeneratedFile(
            path=file_path,
            content=content,
            description=f"SWR hooks for {tag_display_name}",
        )

    def generate_hooks_index_file(self, module_names: list[str]) -> GeneratedFile:
        """Generate index.ts for hooks folder."""
        lines = []

        lines.append("/**")
        lines.append(" * SWR Hooks - React hooks for data fetching")
        lines.append(" *")
        lines.append(" * Auto-generated from OpenAPI specification.")
        lines.append(" * These hooks use SWR for data fetching and caching.")
        lines.append(" *")
        lines.append(" * Usage:")
        lines.append(" * ```typescript")
        lines.append(" * import { useShopProducts } from './_utils/hooks'")
        lines.append(" *")
        lines.append(" * function ProductsPage() {")
        lines.append(" *   const { data, error } = useShopProducts({ page: 1 })")
        lines.append(" *   if (error) return <Error />")
        lines.append(" *   if (!data) return <Loading />")
        lines.append(" *   return <ProductList products={data.results} />")
        lines.append(" * }")
        lines.append(" * ```")
        lines.append(" */")
        lines.append("")

        for module_name in module_names:
            lines.append(f"export * from './{module_name}'")

        lines.append("")

        content = "\n".join(lines)

        return GeneratedFile(
            path="_utils/hooks/index.ts",
            content=content,
            description="Index file for SWR hooks",
        )
