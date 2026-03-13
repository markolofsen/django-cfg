"""
Request body validation mixin — detects OpenAPI schema bugs that would
produce incorrect TypeScript hook signatures.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from ...ir import IROperationObject
from ._errors import raise_if_errors


@dataclass(frozen=True)
class ValidationContext:
    """
    Cross-operation context passed to every rule's check and message callables.

    Attributes:
        list_response_schemas: Schema names that appear as GET response bodies.
            A POST body using one of these is almost certainly a drf-spectacular bug.
    """
    list_response_schemas: frozenset[str]


@dataclass(frozen=True)
class BodyValidationRule:
    """
    A single request body validation rule.

    Attributes:
        name:        Short identifier (used in logs/tests).
        description: Human-readable description of what the rule guards against.
        check:       (op, ctx) → True when a VIOLATION is detected.
        message:     (op, schema_name) → formatted error string shown to the developer.
        blocking:    If True the rule short-circuits — no further rules are checked
                     for this operation once it fires. Use for definitive bugs
                     (DELETE with body, cancel with body). Non-blocking rules
                     (advisory) accumulate alongside other matches.
    """
    name: str
    description: str
    check: Callable[[IROperationObject, ValidationContext], bool]
    message: Callable[[IROperationObject, str], str]
    blocking: bool = True


# ---------------------------------------------------------------------------
# Rule registry
# Rules are evaluated in order. Blocking rules short-circuit on first match.
# Non-blocking rules are always checked (unless a blocking rule fired first).
# ---------------------------------------------------------------------------

_RULES: list[BodyValidationRule] = [
    BodyValidationRule(
        name="delete_with_body",
        description="DELETE endpoints must never carry a requestBody.",
        check=lambda op, ctx: op.http_method == "DELETE",
        message=lambda op, schema: (
            f"\n  [{op.operation_id}] DELETE {op.path}\n"
            f"    Bug: DELETE endpoints must not have a requestBody (got '{schema}').\n"
            f"    Fix: Add request=None to @extend_schema on this view."
        ),
        blocking=True,
    ),
    BodyValidationRule(
        name="cancel_with_body",
        description="Cancel actions must not have a requestBody.",
        check=lambda op, ctx: (
            op.http_method == "POST" and (
                "cancel" in op.operation_id.lower()
                or op.path.rstrip("/").endswith("/cancel")
            )
        ),
        message=lambda op, schema: (
            f"\n  [{op.operation_id}] POST {op.path}\n"
            f"    Bug: Cancel action has requestBody '{schema}' — cancel endpoints take no body.\n"
            f"    Fix: Add request=None to @extend_schema on this view."
        ),
        blocking=True,
    ),
    BodyValidationRule(
        name="get_response_schema_as_body",
        description="GET response schema leaked into a write endpoint's requestBody.",
        check=lambda op, ctx: (
            op.request_body is not None
            and op.request_body.schema_name in ctx.list_response_schemas
        ),
        message=lambda op, schema: (
            f"\n  [{op.operation_id}] {op.http_method} {op.path}\n"
            f"    Bug: requestBody uses '{schema}' which is a GET response schema, not a request schema.\n"
            f"    Fix: Check serializer_class / get_serializer_class() on this view,\n"
            f"         or add request=<CorrectSerializer> to @extend_schema."
        ),
        blocking=True,
    ),
    BodyValidationRule(
        name="response_schema_as_body",
        description="Response schema used as request body (missing 'Request' suffix).",
        check=lambda op, ctx: (
            op.request_body is not None
            and op.request_body.content_type == "application/json"
            and op.request_body.schema_name != "UnknownRequest"
            and not op.request_body.schema_name.endswith("Request")
            and not op.request_body.schema_name.startswith("Patched")
        ),
        message=lambda op, schema: (
            f"\n  [{op.operation_id}] {op.http_method} {op.path}\n"
            f"    Bug: requestBody uses '{schema}' which looks like a response schema (no 'Request' suffix).\n"
            f"    Fix: Ensure COMPONENT_SPLIT_REQUEST=True in Django settings and the view\n"
            f"         uses a separate *Request serializer for writes.\n"
            f"         Or add request=<CorrectSerializer> to @extend_schema."
        ),
        blocking=False,
    ),
]


class RequestBodyValidatorMixin:
    """
    Validates request bodies after all operations are parsed.

    Raises ValueError (hard stop) when drf-spectacular has auto-attached
    a wrong requestBody to an endpoint that shouldn't have one.
    """

    def _validate_request_bodies(self, operations: dict[str, IROperationObject]) -> None:
        ctx = ValidationContext(
            list_response_schemas=frozenset(
                response.schema_name
                for op in operations.values()
                if op.http_method == "GET"
                for response in op.responses.values()
                if response.schema_name
            )
        )

        errors: list[str] = []

        for op in operations.values():
            if op.request_body is None:
                continue
            schema_name = op.request_body.schema_name

            for rule in _RULES:
                if rule.check(op, ctx):
                    errors.append(rule.message(op, schema_name))
                    if rule.blocking:
                        break

        raise_if_errors(errors, "request body")
