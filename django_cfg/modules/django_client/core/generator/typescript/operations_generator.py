"""
TypeScript Operations Generator - Generates TypeScript async operation methods.
"""

from __future__ import annotations

from jinja2 import Environment

from ...ir import IROperationObject
from ...types import FieldType, TypeMapper
from ...types.content_type import ContentType
from ...utils import header_to_param_name, to_camel_case
from .naming import operation_to_method_name


class OperationsGenerator:
    """Generates TypeScript async operation methods."""

    def __init__(self, jinja_env: Environment, context, base):
        self.jinja_env = jinja_env
        self.context = context
        self.base = base
        self._type_mapper = TypeMapper()

    def generate_operation(self, operation: IROperationObject, remove_tag_prefix: bool = False, in_subclient: bool = False) -> str:
        """Generate async method for operation."""

        # Get method name using universal logic
        operation_id = operation.operation_id
        if remove_tag_prefix and operation.tags:
            tag = operation.tags[0]
            operation_id = self.base.remove_tag_prefix(operation_id, tag)

        method_name = operation_to_method_name(operation_id, operation.http_method, '', self.base, operation.path)
        request_prefix = "this.client" if in_subclient else "this"

        # Collect flags needed across multiple helpers
        is_multipart: bool = bool(
            (operation.request_body and operation.request_body.content_type == ContentType.MULTIPART)
            or (operation.patch_request_body and operation.patch_request_body.content_type == ContentType.MULTIPART)
        )
        is_binary: bool = bool(
            operation.request_body
            and operation.request_body.content_type == ContentType.OCTET_STREAM
        )

        params, header_params_list, query_params_list = self._build_method_params(
            operation, is_multipart, is_binary
        )

        return_type = self._build_return_type(operation)

        overload_signatures, use_rest_params, signature = self._build_method_signature(
            method_name, params, query_params_list, return_type
        )

        comment = self._build_docstring(operation)

        body_lines = self._build_body(
            operation, request_prefix,
            header_params_list, query_params_list,
            is_multipart, is_binary, use_rest_params, return_type
        )

        return self._assemble_method(overload_signatures, comment, signature, body_lines)

    # ---------------------------------------------------------------------------
    # Private helpers
    # ---------------------------------------------------------------------------

    def _build_method_params(
        self,
        operation: IROperationObject,
        is_multipart: bool,
        is_binary: bool,
    ) -> tuple[list[str], list[tuple], list[tuple]]:
        """Build the full method parameter list.

        Returns:
            params: ordered list of TypeScript parameter strings
            header_params_list: list of (header_name, ts_param_name, type, required)
            query_params_list: list of (param_name, type, required)
        """
        params = []

        # Path parameters
        for param in operation.path_parameters:
            param_type = self._map_param_type(param.schema_type)
            params.append(f"{param.name}: {param_type}")

        # Request body parameter
        if operation.request_body:
            schema_name = operation.request_body.schema_name
            if schema_name and schema_name in self.context.schemas:
                params.append(f"data: Models.{schema_name}")
            else:
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

        # Header parameters — required first, then optional
        header_params_list = []
        required_header_params = []
        optional_header_params = []

        for param in operation.header_parameters:
            param_type = self._map_param_type(param.schema_type)
            ts_param_name = self._header_to_param_name(param.name)
            header_params_list.append((param.name, ts_param_name, param_type, param.required))
            if param.required:
                required_header_params.append(f"{ts_param_name}: {param_type}")
            else:
                optional_header_params.append(f"{ts_param_name}?: {param_type}")

        params.extend(required_header_params)
        params.extend(optional_header_params)

        # Query parameters — required first, then optional; skip duplicates of path params
        path_param_names = {p.name for p in operation.path_parameters}
        query_params_list = []
        required_query_params = []
        optional_query_params = []

        for param in operation.query_parameters:
            if param.name in path_param_names:
                continue
            param_type = self._map_param_type(param.schema_type)
            query_params_list.append((param.name, param_type, param.required))
            if param.required:
                required_query_params.append(f"{param.name}: {param_type}")
            else:
                optional_query_params.append(f"{param.name}?: {param_type}")

        params.extend(required_query_params)
        params.extend(optional_query_params)

        return params, header_params_list, query_params_list

    def _build_return_type(self, operation: IROperationObject) -> str:
        """Determine the TypeScript return type for the operation."""
        primary_response = operation.primary_success_response
        if primary_response and primary_response.status_code == 204:
            return "void"
        elif primary_response and primary_response.schema_name:
            is_paginated = primary_response.schema_name.startswith('Paginated')
            if operation.is_list_operation and not is_paginated:
                return f"Models.{primary_response.schema_name}[]"
            else:
                return f"Models.{primary_response.schema_name}"
        elif primary_response and primary_response.content_type:
            return "any"
        else:
            return "void"

    def _build_method_signature(
        self,
        method_name: str,
        params: list[str],
        query_params_list: list[tuple],
        return_type: str,
    ) -> tuple[list[str], bool, str]:
        """Build overload signatures and the implementation signature.

        Returns:
            overload_signatures: list of overload strings (may be empty)
            use_rest_params: whether the implementation should use ...args
            signature: the implementation signature line (with opening brace)
        """
        overload_signatures = []
        use_rest_params = False

        if query_params_list:
            # Overload 1: separate parameters (backward compatible)
            overload_signatures.append(f"async {method_name}({', '.join(params)}): Promise<{return_type}>")

            # Overload 2: params object
            params_obj = [p for p in params if not any(
                p.startswith(f"{pn}:") or p.startswith(f"{pn}?:")
                for pn, _, _ in query_params_list
            )]
            query_fields = []
            for param_name, param_type, required in query_params_list:
                optional = "?" if not required else ""
                query_fields.append(f"{param_name}{optional}: {param_type}")
            if query_fields:
                has_required = any(required for _, _, required in query_params_list)
                params_optional = "" if has_required else "?"
                params_obj.append(f"params{params_optional}: {{ {'; '.join(query_fields)} }}")
            overload_signatures.append(f"async {method_name}({', '.join(params_obj)}): Promise<{return_type}>")

            use_rest_params = True

        if use_rest_params:
            signature = f"async {method_name}(...args: any[]): Promise<{return_type}> {{"
        else:
            signature = f"async {method_name}({', '.join(params)}): Promise<{return_type}> {{"

        return overload_signatures, use_rest_params, signature

    def _build_docstring(self, operation: IROperationObject) -> str | None:
        """Build a JSDoc comment string for the operation, or None if empty."""
        comment_lines = []
        if operation.summary:
            comment_lines.append(operation.summary)
        if operation.description:
            if comment_lines:
                comment_lines.append("")
            comment_lines.extend(self.base.wrap_comment(operation.description, 72))

        if not comment_lines:
            return None
        return "/**\n * " + "\n * ".join(comment_lines) + "\n */"

    def _build_url_expr(self, operation: IROperationObject) -> str:
        """Build the path/URL expression (plain string or template literal)."""
        if operation.path_parameters:
            path_with_vars = operation.path
            for param in operation.path_parameters:
                path_with_vars = path_with_vars.replace(f"{{{param.name}}}", f"${{{param.name}}}")
            return f'`{path_with_vars}`'
        return f'"{operation.path}"'

    def _build_headers(self, header_params_list: list[tuple]) -> list[str]:
        """Build header-related body lines.

        Returns lines to emit; also returns whether headers var was created
        (caller checks header_params_list directly to add 'headers' to request_opts).
        """
        if not header_params_list:
            return []
        header_items = [
            f"'{header_name}': String({ts_param_name})"
            for header_name, ts_param_name, _, _ in header_params_list
        ]
        return [f"const headers = {{ {', '.join(header_items)} }};"]

    def _build_query_params_lines(
        self,
        operation: IROperationObject,
        query_params_list: list[tuple],
        use_rest_params: bool,
    ) -> list[str]:
        """Build body lines that handle query parameter extraction."""
        if not query_params_list:
            return []

        param_names = [pn for pn, _, _ in query_params_list]
        lines = []

        if use_rest_params:
            path_params_count = len(operation.path_parameters)
            body_params_count = 1 if (operation.request_body or operation.patch_request_body) else 0
            first_query_pos = path_params_count + body_params_count

            lines.append("let params;")
            lines.append("if (isParamsObject) {")
            lines.append(f"  params = args[{first_query_pos}];")
            lines.append("} else {")
            sorted_query = sorted(query_params_list, key=lambda x: (not x[2], param_names.index(x[0])))
            param_extractions = [
                f"{pn}: args[{first_query_pos + i}]"
                for i, (pn, _, _) in enumerate(sorted_query)
            ]
            lines.append(f"  params = {{ {', '.join(param_extractions)} }};")
            lines.append("}")
        else:
            query_items = ", ".join(param_names)
            lines.append(f"const params = {{ {query_items} }};")

        return lines

    def _build_request_body(
        self,
        operation: IROperationObject,
        is_multipart: bool,
        is_binary: bool,
    ) -> tuple[list[str], str | None]:
        """Build body lines for request body handling.

        Returns:
            lines: code lines to emit
            request_opts_entry: string to add to request_opts (e.g. 'formData', 'body: data'),
                                 or None if no body.
        """
        if not (operation.request_body or operation.patch_request_body):
            return [], None

        req_body = operation.request_body or operation.patch_request_body

        if is_multipart and req_body:
            schema_name = req_body.schema_name
            if schema_name and schema_name in self.context.schemas:
                schema = self.context.schemas[schema_name]
                lines = ["const formData = new FormData();"]
                for prop_name, prop in schema.properties.items():
                    if prop.format == "binary":
                        if prop_name not in schema.required_set:
                            lines.append(f"if (data.{prop_name} !== undefined) formData.append('{prop_name}', data.{prop_name});")
                        else:
                            lines.append(f"formData.append('{prop_name}', data.{prop_name});")
                    elif prop_name in schema.required_set or True:
                        if prop_name not in schema.required_set:
                            lines.append(f"if (data.{prop_name} !== undefined) formData.append('{prop_name}', String(data.{prop_name}));")
                        else:
                            lines.append(f"formData.append('{prop_name}', String(data.{prop_name}));")
                return lines, "formData"
            else:
                return [], "formData: data"

        if is_binary:
            return [], "binaryBody: data"

        return [], "body: data"

    def _build_response_parsing(
        self,
        operation: IROperationObject,
        return_type: str,
        request_prefix: str,
        path_expr: str,
        request_opts: list[str],
    ) -> list[str]:
        """Build the request call and response handling lines."""
        lines = []

        if request_opts:
            lines.append(
                f"const response = await {request_prefix}.request("
                f"'{operation.http_method}', {path_expr}, "
                f"{{ {', '.join(request_opts)} }});"
            )
        else:
            lines.append(
                f"const response = await {request_prefix}.request("
                f"'{operation.http_method}', {path_expr});"
            )

        primary_response = operation.primary_success_response
        if operation.is_list_operation and primary_response:
            is_paginated = primary_response.schema_name and primary_response.schema_name.startswith('Paginated')
            custom_list_schemas = ['ServiceList', 'MethodList', 'TimelineData']
            is_custom_list = primary_response.schema_name in custom_list_schemas if primary_response.schema_name else False

            if is_paginated:
                lines.append("return response;")
            elif is_custom_list:
                lines.append("return response;")
            else:
                lines.append("return (response as any).results || response;")
        elif return_type == "void":
            lines.append("return;")
        else:
            lines.append("return response;")

        return lines

    def _build_body(
        self,
        operation: IROperationObject,
        request_prefix: str,
        header_params_list: list[tuple],
        query_params_list: list[tuple],
        is_multipart: bool,
        is_binary: bool,
        use_rest_params: bool,
        return_type: str,
    ) -> list[str]:
        """Assemble the complete method body lines."""
        body_lines = []
        request_opts = []

        # Args extraction (only when overloaded rest params are used)
        if use_rest_params and query_params_list:
            path_params_count = len(operation.path_parameters)
            body_params_count = 1 if (operation.request_body or operation.patch_request_body) else 0
            first_query_pos = path_params_count + body_params_count

            for i, param in enumerate(operation.path_parameters):
                body_lines.append(f"const {param.name} = args[{i}];")

            if operation.request_body or operation.patch_request_body:
                body_lines.append(f"const data = args[{path_params_count}];")

            body_lines.append(
                f"const isParamsObject = args.length === {first_query_pos + 1} && "
                f"typeof args[{first_query_pos}] === 'object' && "
                f"args[{first_query_pos}] !== null && "
                f"!Array.isArray(args[{first_query_pos}]);"
            )
            body_lines.append("")

        # URL expression
        path_expr = self._build_url_expr(operation)

        # Headers
        header_lines = self._build_headers(header_params_list)
        body_lines.extend(header_lines)
        if header_params_list:
            request_opts.append("headers")

        # Query params
        query_lines = self._build_query_params_lines(operation, query_params_list, use_rest_params)
        body_lines.extend(query_lines)
        if query_params_list:
            request_opts.append("params")

        # Request body
        body_body_lines, body_opts_entry = self._build_request_body(operation, is_multipart, is_binary)
        body_lines.extend(body_body_lines)
        if body_opts_entry:
            request_opts.append(body_opts_entry)

        # Request call + response parsing
        response_lines = self._build_response_parsing(operation, return_type, request_prefix, path_expr, request_opts)
        body_lines.extend(response_lines)

        return body_lines

    def _assemble_method(
        self,
        overload_signatures: list[str],
        comment: str | None,
        signature: str,
        body_lines: list[str],
    ) -> str:
        """Assemble overloads, docstring, signature, and body into the final method string."""
        lines = []

        if overload_signatures:
            for overload_sig in overload_signatures:
                lines.append("  " + overload_sig + ";")
            lines.append("")

        if comment:
            for line in comment.split('\n'):
                lines.append("  " + line)

        lines.append("  " + signature)

        for line in body_lines:
            lines.append("    " + line)

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

        # Add query parameters (skip those that duplicate path params)
        path_param_names = {p.name for p in operation.path_parameters}
        query_params_list = []
        required_query_params = []
        optional_query_params = []

        for param in operation.query_parameters:
            # Skip if this query param name already exists as path param
            if param.name in path_param_names:
                continue
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
        """Map parameter schema type to TypeScript type using unified TypeMapper."""
        try:
            ft = FieldType(schema_type)
            ts_type = self._type_mapper.to_typescript(ft)
            # Handle array special case for params (any[] instead of Array<any>)
            if ft == FieldType.ARRAY:
                return "any[]"
            return ts_type
        except ValueError:
            return "any"

    def _to_camel_case(self, snake_str: str) -> str:
        """Convert snake_case to camelCase. Delegates to shared utility."""
        return to_camel_case(snake_str)

    def _header_to_param_name(self, header_name: str) -> str:
        """Convert HTTP header name to camelCase parameter name. Delegates to shared utility."""
        return header_to_param_name(header_name)
