"""
Operations Generator - Generates operation methods for async and sync clients.

Handles:
- Async operation methods (async def with await)
- Sync operation methods (def without await)
- Path parameters, query parameters, request bodies
- Response parsing and validation
- Multipart/form-data file uploads
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from jinja2 import Environment

from ...ir import IROperationObject

if TYPE_CHECKING:
    from ...ir import IRSchemaObject


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

        # Return type - handle multiple response types
        has_multiple_responses = self._has_multiple_response_types(operation)
        primary_response = operation.primary_success_response

        if has_multiple_responses:
            return_type, response_schemas = self._get_response_type_info(operation)
        elif primary_response and primary_response.schema_name:
            if operation.is_list_operation:
                return_type = f"list[{primary_response.schema_name}]"
            else:
                return_type = primary_response.schema_name
            response_schemas = []
        elif primary_response and primary_response.is_array and primary_response.items_schema_name:
            # Array response with items $ref
            return_type = f"list[{primary_response.items_schema_name}]"
            response_schemas = []
        else:
            return_type = "None"
            response_schemas = []

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

        # Query params - build multiline dict if needed
        if operation.query_parameters:
            if len(operation.query_parameters) <= 2:
                # Inline for few params
                query_items = []
                for param in operation.query_parameters:
                    if param.required:
                        query_items.append(f'"{param.name}": {param.name}')
                    else:
                        query_items.append(f'"{param.name}": {param.name} if {param.name} is not None else None')
                query_dict = "{" + ", ".join(query_items) + "}"
                request_kwargs.append(f"params={query_dict}")
            else:
                # Multiline for many params
                body_lines.append("_params = {")
                for param in operation.query_parameters:
                    if param.required:
                        body_lines.append(f'    "{param.name}": {param.name},')
                    else:
                        body_lines.append(f'    "{param.name}": {param.name} if {param.name} is not None else None,')
                body_lines.append("}")
                request_kwargs.append("params=_params")

        # Check if multipart
        is_multipart = self._is_multipart_operation(operation)

        # Request body
        if operation.request_body:
            if is_multipart:
                # Multipart form data - add file/data building code
                body_lines.extend(self._generate_multipart_body_lines(operation))
                request_kwargs.append("files=_files if _files else None")
                request_kwargs.append("data=_form_data if _form_data else None")
            else:
                # JSON body
                request_kwargs.append("json=data.model_dump(exclude_unset=True)")
        elif operation.patch_request_body:
            # Optional PATCH body - build json separately to avoid long lines
            body_lines.append("_json = data.model_dump(exclude_unset=True) if data else None")
            request_kwargs.append("json=_json")

        # Make request
        method_lower = operation.http_method.lower()
        request_line = f"response = await self._client.{method_lower}(url"
        if request_kwargs:
            request_line += ", " + ", ".join(request_kwargs)
        request_line += ")"

        body_lines.append(request_line)

        # Handle response with detailed error
        body_lines.append("if not response.is_success:")
        body_lines.append("    try:")
        body_lines.append("        error_body = response.json()")
        body_lines.append("    except Exception:")
        body_lines.append("        error_body = response.text")
        body_lines.append('    msg = f"{response.status_code}: {error_body}"')
        body_lines.append("    raise httpx.HTTPStatusError(")
        body_lines.append("        msg, request=response.request, response=response"  )
        body_lines.append("    )")

        if return_type != "None":
            if has_multiple_responses and response_schemas:
                # Multiple response types - check status code
                for i, (status_code, schema_name) in enumerate(response_schemas):
                    if i == 0:
                        body_lines.append(f"if response.status_code == {status_code}:")
                    else:
                        body_lines.append(f"elif response.status_code == {status_code}:")
                    body_lines.append(f"    return {schema_name}.model_validate(response.json())")
                # Default fallback to first schema
                body_lines.append("else:")
                body_lines.append(f"    return {response_schemas[0][1]}.model_validate(response.json())")
            elif primary_response and primary_response.is_array and primary_response.items_schema_name:
                # Array response - parse each item
                item_schema = primary_response.items_schema_name
                body_lines.append(f"return [{item_schema}.model_validate(item) for item in response.json()]")
            elif operation.is_list_operation and primary_response and primary_response.schema_name:
                # Paginated list response - return full paginated object
                body_lines.append(f"return {primary_response.schema_name}.model_validate(response.json())")
            elif primary_response and primary_response.schema_name:
                body_lines.append(f"return {primary_response.schema_name}.model_validate(response.json())")
            else:
                body_lines.append("return response.json()")
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

        # Return type - handle multiple response types
        has_multiple_responses = self._has_multiple_response_types(operation)
        primary_response = operation.primary_success_response

        if has_multiple_responses:
            return_type, response_schemas = self._get_response_type_info(operation)
        elif primary_response and primary_response.schema_name:
            if operation.is_list_operation:
                return_type = f"list[{primary_response.schema_name}]"
            else:
                return_type = primary_response.schema_name
            response_schemas = []
        elif primary_response and primary_response.is_array and primary_response.items_schema_name:
            # Array response with items $ref
            return_type = f"list[{primary_response.items_schema_name}]"
            response_schemas = []
        else:
            return_type = "None"
            response_schemas = []

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

        # Query params - build multiline dict if needed
        if operation.query_parameters:
            if len(operation.query_parameters) <= 2:
                # Inline for few params
                query_items = []
                for param in operation.query_parameters:
                    if param.required:
                        query_items.append(f'"{param.name}": {param.name}')
                    else:
                        query_items.append(f'"{param.name}": {param.name} if {param.name} is not None else None')
                query_dict = "{" + ", ".join(query_items) + "}"
                request_kwargs.append(f"params={query_dict}")
            else:
                # Multiline for many params
                body_lines.append("_params = {")
                for param in operation.query_parameters:
                    if param.required:
                        body_lines.append(f'    "{param.name}": {param.name},')
                    else:
                        body_lines.append(f'    "{param.name}": {param.name} if {param.name} is not None else None,')
                body_lines.append("}")
                request_kwargs.append("params=_params")

        # Check if multipart
        is_multipart = self._is_multipart_operation(operation)

        # Request body
        if operation.request_body:
            if is_multipart:
                # Multipart form data - add file/data building code
                body_lines.extend(self._generate_multipart_body_lines(operation))
                request_kwargs.append("files=_files if _files else None")
                request_kwargs.append("data=_form_data if _form_data else None")
            else:
                # JSON body
                request_kwargs.append("json=data.model_dump(exclude_unset=True)")
        elif operation.patch_request_body:
            # Optional PATCH body - build json separately to avoid long lines
            body_lines.append("_json = data.model_dump(exclude_unset=True) if data else None")
            request_kwargs.append("json=_json")

        # HTTP method
        method_lower = operation.http_method.lower()

        # Build request call (sync version - no await)
        if request_kwargs:
            request_call = f'self._client.{method_lower}(url, {", ".join(request_kwargs)})'
        else:
            request_call = f'self._client.{method_lower}(url)'

        body_lines.append(f"response = {request_call}")

        # Handle response with detailed error
        body_lines.append("if not response.is_success:")
        body_lines.append("    try:")
        body_lines.append("        error_body = response.json()")
        body_lines.append("    except Exception:")
        body_lines.append("        error_body = response.text")
        body_lines.append('    msg = f"{response.status_code}: {error_body}"')
        body_lines.append("    raise httpx.HTTPStatusError(")
        body_lines.append("        msg, request=response.request, response=response"  )
        body_lines.append("    )")

        # Parse response
        if return_type != "None":
            if has_multiple_responses and response_schemas:
                # Multiple response types - check status code
                for i, (status_code, schema_name) in enumerate(response_schemas):
                    if i == 0:
                        body_lines.append(f"if response.status_code == {status_code}:")
                    else:
                        body_lines.append(f"elif response.status_code == {status_code}:")
                    body_lines.append(f"    return {schema_name}.model_validate(response.json())")
                # Default fallback to first schema
                body_lines.append("else:")
                body_lines.append(f"    return {response_schemas[0][1]}.model_validate(response.json())")
            elif primary_response and primary_response.is_array and primary_response.items_schema_name:
                # Array response - parse each item
                item_schema = primary_response.items_schema_name
                body_lines.append(f"return [{item_schema}.model_validate(item) for item in response.json()]")
            elif operation.is_list_operation and primary_response and primary_response.schema_name:
                # List response - return full paginated object
                primary_schema = primary_response.schema_name
                body_lines.append(f"return {primary_schema}.model_validate(response.json())")
            elif primary_response and primary_response.schema_name:
                # Single object response
                body_lines.append(f"return {primary_response.schema_name}.model_validate(response.json())")
            else:
                body_lines.append("return response.json()")

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

    def _is_multipart_operation(self, operation: IROperationObject) -> bool:
        """Check if operation uses multipart/form-data content type."""
        return (
            operation.request_body is not None
            and operation.request_body.content_type == "multipart/form-data"
        )

    def _get_schema_for_operation(self, operation: IROperationObject) -> "IRSchemaObject | None":
        """Get the request body schema for an operation."""
        if not operation.request_body or not operation.request_body.schema_name:
            return None
        schema_name = operation.request_body.schema_name
        # Access schemas through base generator's context
        if hasattr(self.base, 'context') and schema_name in self.base.context.schemas:
            return self.base.context.schemas[schema_name]
        return None

    def _has_multiple_response_types(self, operation: IROperationObject) -> bool:
        """Check if operation has multiple success responses with different schemas."""
        success_responses = operation.success_responses
        if len(success_responses) < 2:
            return False
        # Check if schemas are different
        schemas = set()
        for response in success_responses.values():
            if response.schema_name:
                schemas.add(response.schema_name)
        return len(schemas) > 1

    def _get_response_type_info(self, operation: IROperationObject) -> tuple[str, list[tuple[int, str]]]:
        """Get return type and list of (status_code, schema_name) for multiple responses.

        Returns:
            Tuple of (return_type_str, list of (status_code, schema_name) tuples)
        """
        success_responses = operation.success_responses
        response_schemas: list[tuple[int, str]] = []

        for status_code, response in sorted(success_responses.items()):
            if response.schema_name:
                response_schemas.append((status_code, response.schema_name))

        if len(response_schemas) > 1:
            # Union type
            schema_names = [schema for _, schema in response_schemas]
            return_type = " | ".join(schema_names)
            return return_type, response_schemas
        elif response_schemas:
            # Single response type
            return response_schemas[0][1], response_schemas
        else:
            return "None", []

    def _generate_multipart_body_lines(self, operation: IROperationObject) -> list[str]:
        """Generate code for building multipart form data.

        For multipart operations, we need to:
        1. Separate file fields (format: binary) from data fields
        2. Build files dict for file fields
        3. Build data dict for other fields
        4. Use httpx's files= and data= parameters instead of json=

        Returns:
            List of Python code lines for building the request.
        """
        lines = []
        schema = self._get_schema_for_operation(operation)

        if not schema:
            # Fallback: runtime type detection when schema is not available
            lines.append("# Multipart upload (schema not available, using runtime detection)")
            lines.append("import json as _json")
            lines.append("_files = {}")
            lines.append("_form_data = {}")
            lines.append("_raw_data = data.model_dump(exclude_unset=True)")
            lines.append("for key, value in _raw_data.items():")
            lines.append("    if hasattr(value, 'read'):  # File-like object")
            lines.append("        _files[key] = value")
            lines.append("    elif value is None:")
            lines.append("        pass")
            lines.append("    elif hasattr(value, 'value'):  # Enum")
            lines.append("        _form_data[key] = value.value")
            lines.append("    elif isinstance(value, (dict, list)):  # JSON-serializable")
            lines.append("        _form_data[key] = _json.dumps(value)")
            lines.append("    elif isinstance(value, bool):  # Boolean before int check")
            lines.append("        _form_data[key] = str(value).lower()")
            lines.append("    else:")
            lines.append("        _form_data[key] = value")
            return lines

        # Collect file fields and data fields
        file_fields = []
        data_fields = []

        for prop_name, prop_schema in schema.properties.items():
            if prop_schema.is_binary:
                file_fields.append(prop_name)
            else:
                data_fields.append(prop_name)

        # Generate code for file fields
        lines.append("# Build multipart form data")
        lines.append("_files = {}")
        lines.append("_form_data = {}")
        lines.append("_raw_data = data.model_dump(exclude_unset=True)")

        # Handle file fields
        for field in file_fields:
            lines.append(f"if '{field}' in _raw_data and _raw_data['{field}'] is not None:")
            lines.append(f"    _files['{field}'] = _raw_data['{field}']")

        # Check if we need json import for object/array serialization
        needs_json = any(
            schema.properties[f].is_object or schema.properties[f].is_array
            for f in data_fields
        )
        if needs_json:
            lines.append("import json as _json")

        # Handle data fields with type-aware serialization
        for field in data_fields:
            prop_schema = schema.properties[field]
            lines.append(f"if '{field}' in _raw_data and _raw_data['{field}'] is not None:")

            if prop_schema.enum is not None:
                # Enum fields: extract .value for StrEnum/IntEnum
                lines.append(f"    _val = _raw_data['{field}']")
                lines.append(f"    _form_data['{field}'] = _val.value if hasattr(_val, 'value') else _val")
            elif prop_schema.is_object or prop_schema.is_array:
                # Object/array fields: serialize to JSON string
                lines.append(f"    _form_data['{field}'] = _json.dumps(_raw_data['{field}'])")
            elif prop_schema.type == "boolean":
                # Boolean fields: httpx sends Python repr "True"/"False",
                # but Django expects lowercase "true"/"false"
                lines.append(f"    _form_data['{field}'] = str(_raw_data['{field}']).lower()")
            else:
                # Primitive fields (str, int, float): pass through
                lines.append(f"    _form_data['{field}'] = _raw_data['{field}']")

        return lines
