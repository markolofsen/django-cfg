"""
Request body validation mixin — detects OpenAPI schema bugs that would
produce incorrect TypeScript hook signatures.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...ir import IROperationObject


class RequestBodyValidatorMixin:
    """
    Validates request bodies after all operations are parsed.

    Raises ValueError (hard stop) when drf-spectacular has auto-attached
    a wrong requestBody to an endpoint that shouldn't have one.

    Rules:
    1. DELETE must never have a requestBody.
    2. POST with 'cancel' in the operation_id or path must not have a requestBody.
    3. requestBody schema must not be a schema that appears as a GET response
       (list-schema-as-body: leaked serializer from get_serializer_class).
    4. requestBody schema must end with 'Request' or start with 'Patched'
       for JSON bodies (response schema used as request body).
    """

    def _validate_request_bodies(self, operations: dict[str, IROperationObject]) -> None:
        # Collect all schema names used as GET responses — these must not appear as bodies
        list_response_schemas: set[str] = set()
        for op in operations.values():
            if op.http_method == "GET":
                for response in op.responses.values():
                    if response.schema_name:
                        list_response_schemas.add(response.schema_name)

        errors: list[str] = []

        for op_id, op in operations.items():
            body = op.request_body
            if body is None:
                continue

            schema_name = body.schema_name
            method = op.http_method
            path = op.path

            # Rule 1: DELETE must never have a body
            if method == "DELETE":
                errors.append(
                    f"\n  [{op_id}] DELETE {path}\n"
                    f"    Bug: DELETE endpoints must not have a requestBody (got '{schema_name}').\n"
                    f"    Fix: Add request=None to @extend_schema on this view."
                )
                continue

            # Rule 2: Cancel-pattern
            op_id_lower = op_id.lower()
            if method == "POST" and (
                "cancel" in op_id_lower
                or path.rstrip("/").endswith("/cancel")
            ):
                errors.append(
                    f"\n  [{op_id}] POST {path}\n"
                    f"    Bug: Cancel action has requestBody '{schema_name}' — cancel endpoints take no body.\n"
                    f"    Fix: Add request=None to @extend_schema on this view."
                )
                continue

            # Rule 3: GET response schema leaked into request body
            if schema_name in list_response_schemas:
                errors.append(
                    f"\n  [{op_id}] {method} {path}\n"
                    f"    Bug: requestBody uses '{schema_name}' which is a GET response schema, not a request schema.\n"
                    f"    Fix: Check serializer_class / get_serializer_class() on this view,\n"
                    f"         or add request=<CorrectSerializer> to @extend_schema."
                )
                continue

            # Rule 4: Response schema used as request body (no 'Request' suffix)
            if (
                body.content_type == "application/json"
                and schema_name != "UnknownRequest"
                and not schema_name.endswith("Request")
                and not schema_name.startswith("Patched")
            ):
                errors.append(
                    f"\n  [{op_id}] {method} {path}\n"
                    f"    Bug: requestBody uses '{schema_name}' which looks like a response schema (no 'Request' suffix).\n"
                    f"    Fix: Ensure COMPONENT_SPLIT_REQUEST=True in Django settings and the view\n"
                    f"         uses a separate *Request serializer for writes.\n"
                    f"         Or add request=<CorrectSerializer> to @extend_schema."
                )

        if errors:
            error_list = "".join(errors)
            raise ValueError(
                f"OpenAPI schema has {len(errors)} request body bug(s) that would generate incorrect TypeScript hooks."
                f"\n\nFix these issues in Django views before regenerating:"
                f"{error_list}"
                f"\n\nGeneration aborted."
            )
