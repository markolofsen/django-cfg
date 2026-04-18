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

from ...context import ParamsBuilder
from ...ir import IROperationObject
from ...types import FieldType, TypeMapper

if TYPE_CHECKING:
    from ...ir import IRSchemaObject
    from ..base import BaseGenerator


class OperationsGenerator:
    """Generates operation methods for Python clients."""

    def __init__(self, jinja_env: Environment, base_generator: BaseGenerator):
        """
        Initialize operations generator.

        Args:
            jinja_env: Jinja2 environment for templates
            base_generator: Reference to base generator for utility methods
        """
        self.jinja_env = jinja_env
        self.base = base_generator
        self._type_mapper = TypeMapper()

    def generate_async_operation(self, operation: IROperationObject, remove_tag_prefix: bool = False) -> str:
        """Generate async method for operation."""
        method_name = self._resolve_method_name(operation, remove_tag_prefix)
        params = self._build_operation_params(operation)
        return_type, response_schemas, has_multiple_responses, primary_response = self._resolve_return_type(operation)

        docstring = self._build_docstring(operation)
        body_lines = self._build_common_body_lines(operation, is_async=True)
        self._append_response_parsing(body_lines, return_type, has_multiple_responses, response_schemas, primary_response, operation)

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
        method_name = self._resolve_method_name(operation, remove_tag_prefix)
        params = self._build_operation_params(operation)
        return_type, response_schemas, has_multiple_responses, primary_response = self._resolve_return_type(operation)

        docstring = self._build_docstring(operation)
        body_lines = self._build_common_body_lines(operation, is_async=False)
        self._append_response_parsing(body_lines, return_type, has_multiple_responses, response_schemas, primary_response, operation)

        # Render template
        template = self.jinja_env.get_template('client/sync_operation_method.py.jinja')
        return template.render(
            method_name=method_name,
            params=params,
            return_type=return_type,
            body_lines=body_lines,
            docstring=docstring
        )

    # ------------------------------------------------------------------
    # Shared helpers
    # ------------------------------------------------------------------

    def _resolve_method_name(self, operation: IROperationObject, remove_tag_prefix: bool) -> str:
        """Resolve operation method name, optionally stripping the tag prefix."""
        method_name = operation.operation_id
        if remove_tag_prefix and operation.tags:
            tag = operation.tags[0]
            method_name = self.base.remove_tag_prefix(method_name, tag)
        return method_name

    def _build_operation_params(self, operation: IROperationObject) -> list[str]:
        """Build the Python signature parameter list for an operation."""
        params_builder = ParamsBuilder(operation)
        params_ctx = params_builder.for_python()
        return params_ctx["signature_params"]

    def _resolve_return_type(
        self, operation: IROperationObject
    ) -> tuple[str, list, bool, object]:
        """Resolve return type information for an operation.

        Returns:
            Tuple of (return_type, response_schemas, has_multiple_responses, primary_response)
            where response_schemas is a list of (status_code, schema_name) tuples.
        """
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

        return return_type, response_schemas, has_multiple_responses, primary_response

    def _build_docstring(self, operation: IROperationObject) -> str | None:
        """Build docstring text for an operation."""
        docstring_lines = []
        if operation.summary:
            docstring_lines.append(operation.summary)
        if operation.description:
            if docstring_lines:
                docstring_lines.append("")
            docstring_lines.extend(self.base.wrap_comment(operation.description, 72))
        return "\n".join(docstring_lines) if docstring_lines else None

    def _build_common_body_lines(self, operation: IROperationObject, *, is_async: bool) -> list[str]:
        """Build the method body lines shared between async and sync operations.

        Args:
            operation: The IR operation object.
            is_async: When True, generates ``await self._client.method(...)``; when
                False, generates ``self._client.method(...)`` without await.

        Returns:
            List of Python code lines up to and including the error-handling block.
        """
        body_lines = []

        # Build URL
        url_expr = f'"{operation.path}"'
        if operation.path_parameters:
            # Replace {id} with f-string {id}
            url_expr = f'f"{operation.path}"'

        body_lines.append(f"url = {url_expr}")

        # Build request
        request_kwargs = []

        # Query params - filter out None values to avoid sending empty strings
        if operation.query_parameters:
            # Build dict comprehension that filters None values
            body_lines.append("_params = {")
            body_lines.append("    k: v for k, v in {")
            for param in operation.query_parameters:
                body_lines.append(f'        "{param.name}": {param.name},')
            body_lines.append("    }.items() if v is not None")
            body_lines.append("}")
            request_kwargs.append("params=_params")

        # Check if multipart
        is_multipart = operation.is_multipart

        # Request body
        if operation.request_body:
            if is_multipart:
                # Multipart form data - add file/data building code
                body_lines.extend(self._generate_multipart_body_lines(operation))
                request_kwargs.append("files=_files if _files else None")
                request_kwargs.append("data=_form_data if _form_data else None")
            else:
                # JSON body
                request_kwargs.append("json=data.model_dump(mode=\"json\", exclude_unset=True, exclude_none=True)")
        elif operation.patch_request_body:
            # Optional PATCH body - build json separately to avoid long lines
            body_lines.append("_json = data.model_dump(mode=\"json\", exclude_unset=True, exclude_none=True) if data else None")
            request_kwargs.append("json=_json")

        # Make request
        method_lower = operation.http_method.lower()
        if is_async:
            request_line = f"response = await self._client.{method_lower}(url"
            if request_kwargs:
                request_line += ", " + ", ".join(request_kwargs)
            request_line += ")"
        else:
            if request_kwargs:
                request_call = f'self._client.{method_lower}(url, {", ".join(request_kwargs)})'
            else:
                request_call = f'self._client.{method_lower}(url)'
            request_line = f"response = {request_call}"

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

        return body_lines

    def _append_response_parsing(
        self,
        body_lines: list[str],
        return_type: str,
        has_multiple_responses: bool,
        response_schemas: list,
        primary_response,
        operation: IROperationObject | None = None,
    ) -> None:
        """Append response-parsing lines to *body_lines* in place."""
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
            elif operation is not None and operation.is_list_operation and primary_response and primary_response.schema_name:
                # Paginated list response - return full paginated object
                body_lines.append(f"return {primary_response.schema_name}.model_validate(response.json())")
            elif primary_response and primary_response.schema_name:
                body_lines.append(f"return {primary_response.schema_name}.model_validate(response.json())")
            else:
                body_lines.append("return response.json()")
        else:
            body_lines.append("return None")

    # ------------------------------------------------------------------
    # Private utilities
    # ------------------------------------------------------------------

    def _map_param_type(self, schema_type: str) -> str:
        """Map parameter schema type to Python type using unified TypeMapper."""
        try:
            ft = FieldType(schema_type)
            return self._type_mapper.to_python(ft)
        except ValueError:
            return "str"

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
            lines.append("_raw_data = data.model_dump(mode=\"json\", exclude_unset=True, exclude_none=True)")
            lines.append("for key, value in _raw_data.items():")
            lines.append("    if hasattr(value, 'read'):  # File-like object")
            lines.append("        _files[key] = value")
            lines.append("    elif value is None:")
            lines.append("        pass")
            lines.append("    elif hasattr(value, 'value'):  # Enum")
            lines.append("        _form_data[key] = value.value")
            lines.append("    elif isinstance(value, list) and all(isinstance(i, (str, int, float)) for i in value):")
            lines.append("        _form_data[key] = [str(i) for i in value]  # Repeated keys for multipart")
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

        # Handle file fields — access directly on data to preserve binary file objects.
        # model_dump(mode="json") would attempt to UTF-8 encode bytes, breaking binary uploads.
        for field in file_fields:
            lines.append(f"if data.{field} is not None:")
            lines.append(f"    _files['{field}'] = data.{field}")

        # Only dump non-file fields. Pydantic's JSON serializer cannot
        # encode raw bytes (it tries to UTF-8 decode binary content and
        # crashes with UnicodeDecodeError), so file fields must be
        # excluded from the dump even though they're already extracted
        # into ``_files`` above.
        if data_fields:
            if file_fields:
                exclude_repr = "{" + ", ".join(repr(f) for f in file_fields) + "}"
                lines.append(
                    f"_raw_data = data.model_dump("
                    f"mode=\"json\", exclude_unset=True, exclude_none=True, "
                    f"exclude={exclude_repr})"
                )
            else:
                lines.append(
                    "_raw_data = data.model_dump("
                    "mode=\"json\", exclude_unset=True, exclude_none=True)"
                )

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
            elif prop_schema.is_array and prop_schema.items and prop_schema.items.is_primitive:
                # Array of primitives: send as repeated keys for multipart
                # e.g. tags=["a","b"] → tags=a&tags=b
                lines.append(f"    _form_data.setdefault('{field}', [])")
                lines.append(f"    for _item in _raw_data['{field}']:")
                lines.append(f"        _form_data['{field}'].append(str(_item))")
            elif prop_schema.is_object or prop_schema.is_array:
                # Object/array-of-objects fields: serialize to JSON string
                lines.append(f"    _form_data['{field}'] = _json.dumps(_raw_data['{field}'])")
            elif prop_schema.type == "boolean":
                # Boolean fields: httpx sends Python repr "True"/"False",
                # but Django expects lowercase "true"/"false"
                lines.append(f"    _form_data['{field}'] = str(_raw_data['{field}']).lower()")
            else:
                # Primitive fields (str, int, float): pass through
                lines.append(f"    _form_data['{field}'] = _raw_data['{field}']")

        return lines
