"""
TypeScript Operations Generator - Generates TypeScript async operation methods.
"""

from __future__ import annotations

from jinja2 import Environment

from ...ir import IROperationObject
from .naming import operation_to_method_name


class OperationsGenerator:
    """Generates TypeScript async operation methods."""

    def __init__(self, jinja_env: Environment, context, base):
        self.jinja_env = jinja_env
        self.context = context
        self.base = base

    def generate_operation(self, operation: IROperationObject, remove_tag_prefix: bool = False, in_subclient: bool = False) -> str:
        """Generate async method for operation."""

        # Get method name using universal logic
        # For client methods, we use empty prefix to get short names: list, create, retrieve
        operation_id = operation.operation_id
        if remove_tag_prefix and operation.tags:
            # Remove tag prefix using base class method
            tag = operation.tags[0]
            operation_id = self.base.remove_tag_prefix(operation_id, tag)

        # Use universal naming function with empty prefix for client methods
        # Pass path to distinguish custom actions
        method_name = operation_to_method_name(operation_id, operation.http_method, '', self.base, operation.path)

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

        # Check if this is a binary upload operation
        is_binary = (
            operation.request_body
            and operation.request_body.content_type == "application/octet-stream"
        )

        # Add request body parameter
        if operation.request_body:
            # For both JSON and multipart, accept data as typed object
            schema_name = operation.request_body.schema_name
            if schema_name and schema_name in self.context.schemas:
                params.append(f"data: Models.{schema_name}")
            else:
                # Inline schema
                if is_multipart:
                    params.append("data: FormData")
                elif is_binary:
                    params.append("data: Blob | ArrayBuffer")
                else:
                    params.append("data: any")
        elif operation.patch_request_body:
            schema_name = operation.patch_request_body.schema_name
            if schema_name and schema_name in self.context.schemas:
                params.append(f"data?: Models.{schema_name}")
            else:
                params.append("data?: any")

        # Add header parameters
        # TypeScript requires: required params first, then optional params
        header_params_list = []
        required_header_params = []
        optional_header_params = []

        for param in operation.header_parameters:
            param_type = self._map_param_type(param.schema_type)
            # Convert header name to camelCase for TypeScript (X-Chunk-Index -> xChunkIndex)
            ts_param_name = self._header_to_param_name(param.name)
            header_params_list.append((param.name, ts_param_name, param_type, param.required))

            if param.required:
                required_header_params.append(f"{ts_param_name}: {param_type}")
            else:
                optional_header_params.append(f"{ts_param_name}?: {param_type}")

        # Add required first, then optional
        params.extend(required_header_params)
        params.extend(optional_header_params)

        # Add query parameters (old style - separate params)
        # TypeScript requires: required params first, then optional params
        query_params_list = []
        required_query_params = []
        optional_query_params = []

        for param in operation.query_parameters:
            param_type = self._map_param_type(param.schema_type)
            query_params_list.append((param.name, param_type, param.required))

            if param.required:
                required_query_params.append(f"{param.name}: {param_type}")
            else:
                optional_query_params.append(f"{param.name}?: {param_type}")

        # Add required first, then optional
        params.extend(required_query_params)
        params.extend(optional_query_params)

        # Return type
        primary_response = operation.primary_success_response
        if primary_response and primary_response.status_code == 204:
            # 204 No Content - void response
            return_type = "void"
        elif primary_response and primary_response.schema_name:
            # Named schema - typed response
            is_paginated = primary_response.schema_name.startswith('Paginated')
            if operation.is_list_operation and not is_paginated:
                return_type = f"Models.{primary_response.schema_name}[]"
            else:
                return_type = f"Models.{primary_response.schema_name}"
        elif primary_response and primary_response.content_type:
            # Has response content but no named schema - generic object
            # Use 'any' to allow returning response data
            return_type = "any"
        else:
            # No response
            return_type = "void"

        # Build overload signatures if has query params
        overload_signatures = []
        use_rest_params = False

        if query_params_list:
            # Overload 1: separate parameters (current/backward compatible style)
            overload_signatures.append(f"async {method_name}({', '.join(params)}): Promise<{return_type}>")

            # Overload 2: params object (new style)
            # Build params object signature
            params_obj = [p for p in params if not any(p.startswith(f"{pn}:") or p.startswith(f"{pn}?:") for pn, _, _ in query_params_list)]
            query_fields = []
            for param_name, param_type, required in query_params_list:
                optional = "?" if not required else ""
                query_fields.append(f"{param_name}{optional}: {param_type}")
            if query_fields:
                # Check if any query param is required
                # TypeScript doesn't allow required fields in optional objects
                has_required = any(required for _, _, required in query_params_list)
                params_optional = "" if has_required else "?"
                params_obj.append(f"params{params_optional}: {{ {'; '.join(query_fields)} }}")
            overload_signatures.append(f"async {method_name}({', '.join(params_obj)}): Promise<{return_type}>")

            # Implementation signature - use rest params for compatibility
            use_rest_params = True

        # Build implementation signature
        if use_rest_params:
            signature = f"async {method_name}(...args: any[]): Promise<{return_type}> {{"
        else:
            signature = f"async {method_name}({', '.join(params)}): Promise<{return_type}> {{"

        # Comment
        comment_lines = []
        if operation.summary:
            comment_lines.append(operation.summary)
        if operation.description:
            if comment_lines:
                comment_lines.append("")
            comment_lines.extend(self.base.wrap_comment(operation.description, 72))

        comment = "/**\n * " + "\n * ".join(comment_lines) + "\n */" if comment_lines else None

        # Method body
        body_lines = []

        # Handle overloaded parameters if has query params (using rest params)
        if use_rest_params and query_params_list:
            # Extract parameters from args array
            path_params_count = len(operation.path_parameters)
            body_params_count = 1 if (operation.request_body or operation.patch_request_body) else 0
            first_query_pos = path_params_count + body_params_count

            # Extract path parameters
            for i, param in enumerate(operation.path_parameters):
                body_lines.append(f"const {param.name} = args[{i}];")

            # Extract body/data parameter
            if operation.request_body or operation.patch_request_body:
                body_lines.append(f"const data = args[{path_params_count}];")

            # Check if first query arg is object (params style) or primitive (old style)
            body_lines.append(f"const isParamsObject = args.length === {first_query_pos + 1} && typeof args[{first_query_pos}] === 'object' && args[{first_query_pos}] !== null && !Array.isArray(args[{first_query_pos}]);")
            body_lines.append("")

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

        # Header params
        if header_params_list:
            header_items = []
            for header_name, ts_param_name, _, _ in header_params_list:
                # Map param name to original header name
                header_items.append(f"'{header_name}': String({ts_param_name})")
            body_lines.append(f"const headers = {{ {', '.join(header_items)} }};")
            request_opts.append("headers")

        # Query params
        if query_params_list:
            param_names = [param_name for param_name, _, _ in query_params_list]

            if use_rest_params:
                # Extract params from args array - handle both calling styles
                path_params_count = len(operation.path_parameters)
                body_params_count = 1 if (operation.request_body or operation.patch_request_body) else 0
                first_query_pos = path_params_count + body_params_count

                body_lines.append("let params;")
                body_lines.append("if (isParamsObject) {")
                # Params object style
                body_lines.append(f"  params = args[{first_query_pos}];")
                body_lines.append("} else {")
                # Separate params style - collect from individual args
                param_extractions = []
                for i, param_name in enumerate(param_names):
                    param_extractions.append(f"{param_name}: args[{first_query_pos + i}]")
                body_lines.append(f"  params = {{ {', '.join(param_extractions)} }};")
                body_lines.append("}")
            else:
                # No overloads - standard query params
                query_items = ", ".join(param_names)
                body_lines.append(f"const params = {{ {query_items} }};")

            request_opts.append("params")

        # Body / FormData / Binary
        if operation.request_body or operation.patch_request_body:
            if is_multipart and operation.request_body:
                # Build FormData for multipart upload
                schema_name = operation.request_body.schema_name
                if schema_name and schema_name in self.context.schemas:
                    schema = self.context.schemas[schema_name]
                    body_lines.append("const formData = new FormData();")
                    for prop_name, prop in schema.properties.items():
                        if prop.format == "binary":
                            # Append file
                            body_lines.append(f"formData.append('{prop_name}', data.{prop_name});")
                        elif prop_name in schema.required or True:  # Append all non-undefined fields
                            # Append other fields (wrap in if check for optional)
                            if prop_name not in schema.required:
                                body_lines.append(f"if (data.{prop_name} !== undefined) formData.append('{prop_name}', String(data.{prop_name}));")
                            else:
                                body_lines.append(f"formData.append('{prop_name}', String(data.{prop_name}));")
                    request_opts.append("formData")
                else:
                    # Inline schema - data is already FormData
                    request_opts.append("formData: data")
            elif is_binary:
                # Binary upload - pass raw data with octet-stream content type
                request_opts.append("binaryBody: data")
            else:
                # JSON body
                request_opts.append("body: data")

        # Make request (no type argument when client is 'any')
        if request_opts:
            request_line = f"const response = await {request_prefix}.request('{operation.http_method}', {path_expr}, {{ {', '.join(request_opts)} }});"
        else:
            request_line = f"const response = await {request_prefix}.request('{operation.http_method}', {path_expr});"

        body_lines.append(request_line)

        # Handle response
        if operation.is_list_operation and primary_response:
            # Check if response is paginated
            is_paginated = primary_response.schema_name and primary_response.schema_name.startswith('Paginated')

            # List of custom list response schemas that return objects with array fields (not DRF pagination)
            # These return {items: [], total: N} instead of {results: [], count: N, ...}
            custom_list_schemas = ['ServiceList', 'MethodList', 'TimelineData']
            is_custom_list = primary_response.schema_name in custom_list_schemas if primary_response.schema_name else False

            if is_paginated:
                # Return full DRF paginated response object {count, results, next, previous, ...}
                body_lines.append("return response;")
            elif is_custom_list:
                # Return full custom list response object {services: [], total_services: N}
                body_lines.append("return response;")
            else:
                # Fallback: try to extract results field (for unknown list responses)
                body_lines.append("return (response as any).results || response;")
        elif return_type == "void":
            # No content response (204 No Content or truly void)
            body_lines.append("return;")
        else:
            # Return response data
            body_lines.append("return response;")

        # Build method with proper class-level indentation (2 spaces)
        lines = []

        # Add overload signatures first (if any)
        if overload_signatures:
            for overload_sig in overload_signatures:
                lines.append("  " + overload_sig + ";")
            lines.append("")  # Empty line between overloads and implementation

        # Add comment with indentation
        if comment:
            comment_lines_formatted = []
            for line in comment.split('\n'):
                comment_lines_formatted.append("  " + line)
            lines.extend(comment_lines_formatted)

        # Add signature with indentation
        lines.append("  " + signature)

        # Add body with indentation (4 spaces total: 2 for class + 2 for method body)
        for line in body_lines:
            lines.append("    " + line)

        # Add closing brace with indentation
        lines.append("  " + "}")

        return "\n".join(lines)

    def generate_url_method(self, operation: IROperationObject, remove_tag_prefix: bool = False, in_subclient: bool = False) -> str:
        """Generate URL builder method for streaming/download operations.

        Generates a method like `streamUrl(session_id, path): string` that returns
        the full URL without making an HTTP request. Useful for:
        - Audio/video streaming (browser handles Range requests)
        - File downloads
        - SSE endpoints
        """
        # Get method name
        operation_id = operation.operation_id
        if remove_tag_prefix and operation.tags:
            tag = operation.tags[0]
            operation_id = self.base.remove_tag_prefix(operation_id, tag)

        base_method_name = operation_to_method_name(operation_id, operation.http_method, '', self.base, operation.path)
        method_name = f"{base_method_name}Url"

        # Client reference prefix
        client_prefix = "this.client" if in_subclient else "this"

        # Method parameters (path params + query params)
        params = []

        # Add path parameters
        for param in operation.path_parameters:
            param_type = self._map_param_type(param.schema_type)
            params.append(f"{param.name}: {param_type}")

        # Add query parameters
        query_params_list = []
        required_query_params = []
        optional_query_params = []

        for param in operation.query_parameters:
            param_type = self._map_param_type(param.schema_type)
            query_params_list.append((param.name, param_type, param.required))

            if param.required:
                required_query_params.append(f"{param.name}: {param_type}")
            else:
                optional_query_params.append(f"{param.name}?: {param_type}")

        params.extend(required_query_params)
        params.extend(optional_query_params)

        # Build path expression
        path_expr = f'"{operation.path}"'
        if operation.path_parameters:
            path_with_vars = operation.path
            for param in operation.path_parameters:
                path_with_vars = path_with_vars.replace(f"{{{param.name}}}", f"${{{param.name}}}")
            path_expr = f'`{path_with_vars}`'

        # Build method
        lines = []

        # Filter out 'token' from query params - we auto-inject it from client
        filtered_query_params = [(name, type_, req) for name, type_, req in query_params_list if name != 'token']
        # Also filter 'token' from method signature params
        filtered_params = [p for p in params if not p.startswith('token')]

        # Comment
        comment = f"/**\n * Get URL for {operation.summary or operation_id}\n *\n * Returns the full URL without making a request.\n * Automatically includes JWT token for authentication.\n * Useful for streaming media or downloads.\n */"
        for line in comment.split('\n'):
            lines.append("  " + line)

        # Signature (without token param - it's auto-injected)
        lines.append(f"  {method_name}({', '.join(filtered_params)}): string {{")

        # Build URL with query params
        lines.append(f"    const urlPath = {path_expr};")
        lines.append(f"    const baseUrl = {client_prefix}.getBaseUrl();")
        lines.append(f"    const _authToken = {client_prefix}.getToken();")

        # Always use URLSearchParams to handle token + other query params
        lines.append("    const queryParams = new URLSearchParams();")

        # Add explicit query parameters from operation (excluding token)
        for param_name, _, required in filtered_query_params:
            if required:
                lines.append(f"    queryParams.set('{param_name}', String({param_name}));")
            else:
                lines.append(f"    if ({param_name} !== undefined) queryParams.set('{param_name}', String({param_name}));")

        # Add auto-injected token if available
        lines.append("    if (_authToken) queryParams.set('token', _authToken);")

        lines.append("    const queryString = queryParams.toString();")
        lines.append("    return queryString ? `${baseUrl}${urlPath}?${queryString}` : `${baseUrl}${urlPath}`;")

        lines.append("  }")

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

    def _header_to_param_name(self, header_name: str) -> str:
        """
        Convert HTTP header name to camelCase parameter name.

        Examples:
            >>> self._header_to_param_name("X-Chunk-Index")
            'xChunkIndex'
            >>> self._header_to_param_name("Content-Type")
            'contentType'
            >>> self._header_to_param_name("X-Is-Last")
            'xIsLast'
        """
        # Remove leading/trailing whitespace and split by hyphen
        parts = header_name.strip().split("-")
        if not parts:
            return header_name.lower()
        # First part lowercase, rest title case
        return parts[0].lower() + "".join(p.title() for p in parts[1:])
