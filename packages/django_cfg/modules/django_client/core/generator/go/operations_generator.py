"""
Operations Generator - Generates Go client methods from IR operations.

Handles generation of type-safe client methods for each API operation,
including multipart/form-data file uploads.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .naming import to_pascal_case

if TYPE_CHECKING:
    from jinja2 import Environment

    from ...ir import IRContext, IROperationObject, IRSchemaObject
    from .generator import GoGenerator


class OperationsGenerator:
    """Generates Go client operation methods from IR operations."""

    def __init__(
        self,
        jinja_env: Environment,
        context: IRContext,
        generator: GoGenerator,
    ):
        """
        Initialize operations generator.

        Args:
            jinja_env: Jinja2 environment
            context: IRContext from parser
            generator: Parent GoGenerator instance
        """
        self.jinja_env = jinja_env
        self.context = context
        self.generator = generator

    def generate_operation_method(
        self,
        operation: IROperationObject,
        remove_tag_prefix: bool = False,
    ) -> dict:
        """
        Generate Go method definition for an operation.

        Args:
            operation: IROperationObject to generate
            remove_tag_prefix: Remove tag prefix from operation name

        Returns:
            Dictionary with operation method info
        """
        # Get method name
        op_id = operation.operation_id
        if remove_tag_prefix and operation.tags:
            op_id = self.generator.remove_tag_prefix(op_id, operation.tags[0])

        method_name = to_pascal_case(op_id)

        # Check if multipart operation
        is_multipart = self._is_multipart_operation(operation)

        # Get request/response types
        request_type = None
        if operation.request_body and operation.request_body.schema_name:
            request_type = operation.request_body.schema_name
            # Handle inline request bodies (multipart/form-data, etc.)
            if request_type == "InlineRequestBody":
                request_type = "map[string]interface{}"

        # Get response type - handle array responses
        response_type = "interface{}"
        is_array_response = False
        primary_response = operation.primary_success_response

        if primary_response:
            # Check if response is a simple array (not paginated)
            if primary_response.is_array and primary_response.items_schema_name:
                # Array response: return []ItemType
                response_type = f"[]{primary_response.items_schema_name}"
                is_array_response = True
            elif primary_response.schema_name:
                response_type = primary_response.schema_name
                # For POST/PUT 201 responses: if schema ends with "Create", use "Detail" instead
                # This handles drf-spectacular's COMPONENT_SPLIT_REQUEST_RESPONSE pattern
                # where Create schema only has input fields but API returns full object
                if (
                    operation.http_method.upper() in ("POST", "PUT")
                    and operation.primary_success_status == 201
                    and response_type.endswith("Create")
                ):
                    detail_type = response_type[:-6] + "Detail"  # Replace "Create" with "Detail"
                    if detail_type in self.context.schemas:
                        response_type = detail_type
        elif operation.responses.get("200") and operation.responses["200"].schema_name:
            response_type = operation.responses["200"].schema_name
        elif operation.responses.get("201") and operation.responses["201"].schema_name:
            response_type = operation.responses["201"].schema_name

        # Build parameters
        params = []

        # Path parameters
        for param in operation.parameters:
            if param.location == "path":
                params.append({
                    "name": param.name,
                    "type": self._get_param_go_type(param.schema_type),
                    "location": "path",
                })

        # Query parameters struct (if any)
        query_params = [p for p in operation.parameters if p.location == "query"]
        query_params_struct = None
        if query_params:
            params_struct_name = f"{method_name}Params"
            params.append({
                "name": "params",
                "type": f"*{params_struct_name}",
                "location": "query",
            })

            # Build query params struct definition
            query_params_struct = {
                "name": params_struct_name,
                "fields": [
                    {
                        "name": to_pascal_case(p.name),
                        "type": self._get_param_go_type(p.schema_type),
                        "json_name": p.name,
                        "required": p.required,
                    }
                    for p in query_params
                ]
            }

        # Get multipart field info if applicable
        multipart_fields = None
        if is_multipart:
            multipart_fields = self._get_multipart_fields(operation)

        return {
            "name": method_name,
            "http_method": operation.http_method.upper(),
            "path": operation.path,
            "parameters": params,
            "request_type": request_type,
            "response_type": response_type,
            "description": operation.summary or operation.description or f"{method_name} operation",
            "operation_id": operation.operation_id,
            "query_params_struct": query_params_struct,
            "is_multipart": is_multipart,
            "multipart_fields": multipart_fields,
            "is_array_response": is_array_response,
        }

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
        if schema_name in self.context.schemas:
            return self.context.schemas[schema_name]
        return None

    def _get_multipart_fields(self, operation: IROperationObject) -> dict:
        """
        Get field information for multipart request.

        Returns:
            Dictionary with:
            - file_fields: list of file field names (format: binary)
            - data_fields: list of regular data field names
        """
        schema = self._get_schema_for_operation(operation)
        if not schema:
            # Fallback - assume 'file' is file field
            return {
                "file_fields": [{"name": "file", "go_name": "File", "type": "io.Reader", "required": False}],
                "data_fields": [],
            }

        file_fields = []
        data_fields = []

        for prop_name, prop_schema in schema.properties.items():
            go_name = to_pascal_case(prop_name)
            is_required = prop_name in schema.required
            go_type = self._get_field_go_type(prop_schema, is_required)

            # Detect special field types
            is_array = prop_schema.type == "array"
            is_enum = bool(prop_schema.enum) or (
                prop_schema.ref and "types." in go_type
            )

            field_info = {
                "name": prop_name,
                "go_name": go_name,
                "type": go_type,
                "required": is_required,
                "is_array": is_array,
                "is_enum": is_enum,
            }

            if prop_schema.is_binary:
                file_fields.append(field_info)
            else:
                data_fields.append(field_info)

        return {
            "file_fields": file_fields,
            "data_fields": data_fields,
        }

    def _get_field_go_type(self, prop_schema, required: bool = True) -> str:
        """Get Go type for a schema property."""
        if prop_schema.is_binary:
            # io.Reader is an interface, no pointer needed
            return "io.Reader"

        # Handle object type (maps)
        if prop_schema.type == "object":
            return "map[string]interface{}"

        # Handle array type
        if prop_schema.type == "array":
            # Arrays in Go are slices, no pointer needed
            item_type = "string"  # default
            if prop_schema.items:
                item_type = self._get_field_go_type(prop_schema.items, required=True)
            return f"[]{item_type}"

        # Handle enum (ref to types package)
        if prop_schema.enum or prop_schema.ref:
            # This will be handled by type mapper, just return a placeholder
            # The actual type comes from the model
            return "enum"

        type_map = {
            "string": "string",
            "integer": "int64",
            "number": "float64",
            "boolean": "bool",
        }
        base_type = type_map.get(prop_schema.type, "string")

        # Add pointer for optional fields (except maps/interfaces/arrays)
        if not required and base_type not in ["interface{}", "map[string]interface{}"]:
            return f"*{base_type}"
        return base_type

    def _get_param_go_type(self, schema_type: str) -> str:
        """Get Go type for parameter schema type."""
        type_map = {
            "string": "string",
            "integer": "int64",
            "number": "float64",
            "boolean": "bool",
        }
        return type_map.get(schema_type, "string")
