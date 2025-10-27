"""
Operations Generator - Generates Go client methods from IR operations.

Handles generation of type-safe client methods for each API operation.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .naming import to_pascal_case

if TYPE_CHECKING:
    from jinja2 import Environment

    from ...ir import IRContext, IROperationObject
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

        # Get request/response types
        request_type = None
        if operation.request_body and operation.request_body.schema_name:
            request_type = operation.request_body.schema_name
            # Handle inline request bodies (multipart/form-data, etc.)
            if request_type == "InlineRequestBody":
                request_type = "map[string]interface{}"

        response_type = "interface{}"
        if operation.responses.get("200") and operation.responses["200"].schema_name:
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
        }

    def _get_param_go_type(self, schema_type: str) -> str:
        """Get Go type for parameter schema type."""
        type_map = {
            "string": "string",
            "integer": "int64",
            "number": "float64",
            "boolean": "bool",
        }
        return type_map.get(schema_type, "string")
