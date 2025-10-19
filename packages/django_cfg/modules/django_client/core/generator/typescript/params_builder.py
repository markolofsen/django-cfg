"""
Universal parameter builder for TypeScript generators.

This module provides a unified way to build function parameters
for both operations and fetchers, ensuring consistent behavior.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...ir import IROperationObject, IRContext


@dataclass
class ParamInfo:
    """Information about a single parameter."""
    name: str
    type: str
    required: bool
    source: str  # 'path' | 'query' | 'body'


@dataclass
class ParamsStructure:
    """Structured information about all parameters for a function."""

    # Function signature (e.g., "id: number, params: { page?: number }")
    func_signature: str

    # API call arguments (e.g., "id, params?.page")
    api_call_args: str

    # All parameters info
    all_params: list[ParamInfo]

    # Grouped by source
    path_params: list[ParamInfo]
    query_params: list[ParamInfo]
    body_param: ParamInfo | None


class ParamsBuilder:
    """
    Universal builder for TypeScript function parameters.

    Handles:
    - Path parameters (always required)
    - Query parameters (can be required or optional)
    - Request body (can be required or optional)
    - Multipart form data

    Ensures TypeScript rules:
    - Required parameters before optional
    - Optional object cannot contain required fields
    """

    def __init__(self, context: IRContext, type_mapper=None):
        self.context = context
        self.type_mapper = type_mapper or self._default_type_mapper

    def build_params_structure(
        self,
        operation: IROperationObject,
        for_fetcher: bool = False
    ) -> ParamsStructure:
        """
        Build complete parameter structure for an operation.

        Args:
            operation: IR operation object
            for_fetcher: If True, generate for fetcher function (unpacks params)
                        If False, generate for client method (separate params)

        Returns:
            ParamsStructure with all parameter information
        """
        all_params: list[ParamInfo] = []
        func_parts: list[str] = []
        api_call_parts: list[str] = []

        # 1. Path parameters (always first, always required)
        path_params = self._build_path_params(operation)
        all_params.extend(path_params)

        for param in path_params:
            func_parts.append(f"{param.name}: {param.type}")
            api_call_parts.append(param.name)

        # 2. Request body (before query params to match client signature order)
        body_param = self._build_body_param(operation, for_fetcher)
        if body_param:
            all_params.append(body_param)

            if body_param.required:
                func_parts.append(f"{body_param.name}: {body_param.type}")
            else:
                func_parts.append(f"{body_param.name}?: {body_param.type}")

            if for_fetcher:
                # Fetchers pass body as data
                api_call_parts.append(body_param.name)
            else:
                # Client methods may unpack multipart
                api_call_parts.append(body_param.name)

        # 3. Query parameters (last, grouped in params object or separate)
        query_params = self._build_query_params(operation)
        all_params.extend(query_params)

        if query_params:
            if for_fetcher:
                # Fetchers: group in params object, unpack when calling
                func_sig, api_args = self._build_query_for_fetcher(query_params)
                func_parts.append(func_sig)
                api_call_parts.extend(api_args)
            else:
                # Client: separate parameters (required first, then optional)
                for param in query_params:
                    if param.required:
                        func_parts.append(f"{param.name}: {param.type}")
                    else:
                        func_parts.append(f"{param.name}?: {param.type}")
                    api_call_parts.append(param.name)

        return ParamsStructure(
            func_signature=", ".join(func_parts) if func_parts else "",
            api_call_args=", ".join(api_call_parts) if api_call_parts else "",
            all_params=all_params,
            path_params=path_params,
            query_params=query_params,
            body_param=body_param,
        )

    def _build_path_params(self, operation: IROperationObject) -> list[ParamInfo]:
        """Build path parameters (always required)."""
        params = []
        for param in operation.path_parameters:
            params.append(ParamInfo(
                name=param.name,
                type=self.type_mapper(param.schema_type),
                required=True,
                source='path'
            ))
        return params

    def _build_query_params(self, operation: IROperationObject) -> list[ParamInfo]:
        """
        Build query parameters.

        Returns list sorted by: required first, then optional.
        This ensures TypeScript compatibility.
        """
        required_params = []
        optional_params = []

        for param in operation.query_parameters:
            param_info = ParamInfo(
                name=param.name,
                type=self.type_mapper(param.schema_type),
                required=param.required,
                source='query'
            )

            if param.required:
                required_params.append(param_info)
            else:
                optional_params.append(param_info)

        # Required first, then optional
        return required_params + optional_params

    def _build_body_param(
        self,
        operation: IROperationObject,
        for_fetcher: bool
    ) -> ParamInfo | None:
        """Build request body parameter."""
        if operation.request_body:
            schema_name = operation.request_body.schema_name

            # Check if schema exists in components
            if schema_name and schema_name in self.context.schemas:
                body_type = schema_name
            else:
                body_type = "any"

            return ParamInfo(
                name="data",
                type=body_type,
                required=True,  # POST/PUT body is usually required
                source='body'
            )
        elif operation.patch_request_body:
            schema_name = operation.patch_request_body.schema_name

            if schema_name and schema_name in self.context.schemas:
                body_type = schema_name
            else:
                body_type = "any"

            return ParamInfo(
                name="data",
                type=body_type,
                required=False,  # PATCH body is optional
                source='body'
            )

        return None

    def _build_query_for_fetcher(
        self,
        query_params: list[ParamInfo]
    ) -> tuple[str, list[str]]:
        """
        Build query parameters for fetcher function.

        Returns:
            (func_signature, api_call_args)

        Example:
            (
                "params: { instrument: string; limit?: number }",
                ["params.instrument", "params.limit"]
            )
        """
        # Check if any param is required
        has_required = any(p.required for p in query_params)

        # params is required if at least one field is required
        # (TypeScript doesn't allow required fields in optional objects)
        params_optional = "" if has_required else "?"
        params_accessor = "params." if has_required else "params?."

        # Build params object signature
        query_fields = []
        api_args = []

        for param in query_params:
            optional = "?" if not param.required else ""
            query_fields.append(f"{param.name}{optional}: {param.type}")
            api_args.append(f"{params_accessor}{param.name}")

        func_sig = f"params{params_optional}: {{ {'; '.join(query_fields)} }}"

        return (func_sig, api_args)

    def _default_type_mapper(self, schema_type: str) -> str:
        """Map OpenAPI type to TypeScript type."""
        type_map = {
            "integer": "number",
            "number": "number",
            "string": "string",
            "boolean": "boolean",
            "array": "any[]",
            "object": "any",
        }
        return type_map.get(schema_type, "any")
