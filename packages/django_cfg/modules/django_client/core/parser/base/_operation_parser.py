"""
Operation parsing mixin — converts OpenAPI path items to IROperationObjects.
"""

from __future__ import annotations

from ..models import OperationObject, PathItemObject, ParameterObject, RequestBodyObject, ReferenceObject, SchemaObject
from ...ir import IROperationObject, IRParameterObject, IRRequestBodyObject, IRResponseObject
from ...utils.naming import to_pascal_case


class OperationParserMixin:
    """Parses OpenAPI path operations (GET/POST/etc.) to IROperationObjects."""

    def _parse_all_operations(self) -> dict[str, IROperationObject]:
        """Parse all operations from paths."""
        if not self.spec.paths:
            return {}

        operations = {}
        for path, path_item in self.spec.paths.items():
            for method, operation in path_item.operations.items():
                if not operation.operationId:
                    operation.operationId = self._generate_operation_id(method, path)
                op_id = operation.operationId
                operations[op_id] = self._parse_operation(operation, method, path, path_item)
        return operations

    def _parse_operation(
        self,
        operation: OperationObject,
        method: str,
        path: str,
        path_item: PathItemObject,
    ) -> IROperationObject:
        parameters = self._parse_parameters(operation, path_item)

        request_body = None
        patch_request_body = None
        operation_id = operation.operationId or f"{method.lower()}_{path.replace('/', '_').strip('_')}"

        if operation.requestBody:
            if not isinstance(operation.requestBody, ReferenceObject):
                body = self._parse_request_body(operation.requestBody, operation_id)
                if method == "PATCH":
                    patch_request_body = body
                else:
                    request_body = body

        responses = self._parse_responses(operation.responses)

        return IROperationObject(
            operation_id=operation.operationId or "",
            http_method=method,
            path=path,
            summary=operation.summary,
            description=operation.description,
            tags=operation.tags or [],
            parameters=parameters,
            request_body=request_body,
            patch_request_body=patch_request_body,
            responses=responses,
            deprecated=operation.deprecated,
        )

    def _parse_parameters(
        self,
        operation: OperationObject,
        path_item: PathItemObject,
    ) -> list[IRParameterObject]:
        params = []
        for param_or_ref in (path_item.parameters or []):
            if not isinstance(param_or_ref, ReferenceObject):
                params.append(self._parse_parameter(param_or_ref))
        for param_or_ref in (operation.parameters or []):
            if not isinstance(param_or_ref, ReferenceObject):
                params.append(self._parse_parameter(param_or_ref))
        return params

    def _parse_parameter(self, param: ParameterObject) -> IRParameterObject:
        schema_type = "string"
        items_type = None

        if param.schema_:
            if isinstance(param.schema_, SchemaObject):
                schema_type = self._normalize_type(param.schema_)
                if schema_type == "array" and param.schema_.items:
                    if isinstance(param.schema_.items, SchemaObject):
                        items_type = self._normalize_type(param.schema_.items)

        return IRParameterObject(
            name=param.name,
            location=param.in_,
            schema_type=schema_type,
            required=param.required,
            description=param.description,
            default=param.example,
            items_type=items_type,
            deprecated=param.deprecated,
        )

    def _parse_request_body(self, body: RequestBodyObject, operation_id: str) -> IRRequestBodyObject:
        schema_name = None
        content_type = "application/json"

        if body.content:
            content_types = list(body.content.keys())
            if "application/json" in content_types:
                content_type = "application/json"
            elif content_types:
                content_type = content_types[0]

            media_type = body.content.get(content_type)
            if media_type and media_type.schema_:
                if isinstance(media_type.schema_, ReferenceObject):
                    schema_name = media_type.schema_.ref_name
                    if "multipart/form-data" in content_types and self._schema_has_binary_field(schema_name):
                        content_type = "multipart/form-data"
                else:
                    schema_name = to_pascal_case(operation_id) + "Request"
                    inline_schema = self._parse_schema(schema_name, media_type.schema_)
                    inline_schema.is_request_model = True
                    self._inline_schemas[schema_name] = inline_schema

        return IRRequestBodyObject(
            schema_name=schema_name or "UnknownRequest",
            content_type=content_type,
            required=body.required,
            description=body.description,
        )

    def _parse_responses(
        self,
        responses: dict[str, any],
    ) -> dict[int, IRResponseObject]:
        ir_responses = {}
        for status_code_str, response_or_ref in responses.items():
            if status_code_str == "default":
                continue
            try:
                status_code = int(status_code_str)
            except ValueError:
                continue
            if isinstance(response_or_ref, ReferenceObject):
                continue

            schema_name = None
            is_paginated = False
            is_array = False
            items_schema_name = None
            content_type = "application/json"

            if response_or_ref.content:
                for ct, media_type in response_or_ref.content.items():
                    content_type = ct
                    if media_type.schema_:
                        if isinstance(media_type.schema_, ReferenceObject):
                            schema_name = media_type.schema_.ref_name
                            if schema_name.startswith("Paginated"):
                                is_paginated = True
                        elif isinstance(media_type.schema_, SchemaObject):
                            schema_type = self._normalize_type(media_type.schema_)
                            if schema_type == "array" and media_type.schema_.items:
                                is_array = True
                                if isinstance(media_type.schema_.items, ReferenceObject):
                                    items_schema_name = media_type.schema_.items.ref_name
                    break

            ir_responses[status_code] = IRResponseObject(
                status_code=status_code,
                schema_name=schema_name,
                content_type=content_type,
                description=response_or_ref.description,
                is_paginated=is_paginated,
                is_array=is_array,
                items_schema_name=items_schema_name,
            )

        return ir_responses

    def _generate_operation_id(self, method: str, path: str) -> str:
        """Generate fallback operation_id from method + path when missing."""
        parts = [p for p in path.split("/") if p and not p.startswith("{")]
        resource = parts[-1] if parts else "unknown"
        action_map = {
            "GET": "retrieve" if "{" in path else "list",
            "POST": "create",
            "PUT": "update",
            "PATCH": "partial_update",
            "DELETE": "destroy",
        }
        action = action_map.get(method, method.lower())
        return f"{resource}_{action}"
