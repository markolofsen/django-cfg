"""
Operations Generator - Generates operation methods for async and sync clients.

Handles:
- Async operation methods (async def with await)
- Sync operation methods (def without await)
- Path parameters, query parameters, request bodies
- Response parsing and validation
"""

from __future__ import annotations

from jinja2 import Environment

from ...ir import IROperationObject


class OperationsGenerator:
    """Generates operation methods for Python clients."""

    def __init__(self, jinja_env: Environment, base_generator):
        """
        Initialize operations generator.

        Args:
            jinja_env: Jinja2 environment for templates
            base_generator: Reference to base generator for utility methods
        """
        self.jinja_env = jinja_env
        self.base = base_generator

    def generate_async_operation(self, operation: IROperationObject, remove_tag_prefix: bool = False) -> str:
        """Generate async method for operation."""
        # Get method name
        method_name = operation.operation_id
        if remove_tag_prefix and operation.tags:
            # Remove tag prefix using base class method
            tag = operation.tags[0]
            method_name = self.base.remove_tag_prefix(method_name, tag)

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
            docstring_lines.extend(self.base.wrap_comment(operation.description, 72))

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
        if operation.request_body:
            # Required body
            request_kwargs.append("json=data.model_dump()")
        elif operation.patch_request_body:
            # Optional PATCH body - check for None
            request_kwargs.append("json=data.model_dump() if data is not None else None")

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
                # Paginated list response - return full paginated object
                body_lines.append(f"return {primary_response.schema_name}.model_validate(response.json())")
            else:
                body_lines.append(f"return {primary_response.schema_name}.model_validate(response.json())")
        else:
            body_lines.append("return None")

        template = self.jinja_env.get_template('client/operation_method.py.jinja')
        return template.render(
            method_name=method_name,
            params=params,
            return_type=return_type,
            docstring=docstring,
            body_lines=body_lines
        )

    def generate_sync_operation(self, operation: IROperationObject, remove_tag_prefix: bool = False) -> str:
        """Generate sync method for operation (mirrors async generate_operation)."""
        # Get method name
        method_name = operation.operation_id
        if remove_tag_prefix and operation.tags:
            # Remove tag prefix using base class method
            tag = operation.tags[0]
            method_name = self.base.remove_tag_prefix(method_name, tag)

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

        # Docstring
        docstring_lines = []
        if operation.summary:
            docstring_lines.append(operation.summary)
        if operation.description:
            if docstring_lines:
                docstring_lines.append("")
            docstring_lines.extend(self.base.wrap_comment(operation.description, 72))

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
        if operation.request_body:
            # Required body
            request_kwargs.append("json=data.model_dump(exclude_unset=True)")
        elif operation.patch_request_body:
            # Optional PATCH body - check for None
            request_kwargs.append("json=data.model_dump(exclude_unset=True) if data is not None else None")

        # HTTP method
        method_lower = operation.http_method.lower()

        # Build request call (sync version - no await)
        if request_kwargs:
            request_call = f'self._client.{method_lower}(url, {", ".join(request_kwargs)})'
        else:
            request_call = f'self._client.{method_lower}(url)'

        body_lines.append(f"response = {request_call}")
        body_lines.append("response.raise_for_status()")

        # Parse response
        if return_type != "None":
            if operation.is_list_operation:
                # List response - return full paginated object
                primary_schema = primary_response.schema_name
                body_lines.append(f"return {primary_schema}.model_validate(response.json())")
            else:
                # Single object response
                body_lines.append(f"return {return_type}.model_validate(response.json())")

        # Render template
        template = self.jinja_env.get_template('client/sync_operation_method.py.jinja')
        return template.render(
            method_name=method_name,
            params=params,
            return_type=return_type,
            body_lines=body_lines,
            docstring=docstring
        )

    def _map_param_type(self, schema_type: str) -> str:
        """Map parameter schema type to Python type."""
        type_map = {
            "string": "str",
            "integer": "int",
            "number": "float",
            "boolean": "bool",
            "array": "list",
            "object": "dict",
        }
        return type_map.get(schema_type, "str")
