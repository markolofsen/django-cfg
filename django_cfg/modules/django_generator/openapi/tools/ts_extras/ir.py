"""Minimal IR over an OpenAPI 3.1 spec.

The spec produced by FastAPI + sliced by `core.slicer` is what we operate on.
We don't try to be a full OpenAPI parser — only what zod/hooks generators
need. Everything else stays as raw dict in `.raw`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

_HTTP_METHODS = {"get", "put", "post", "delete", "patch"}


@dataclass(slots=True)
class IRSchema:
    """A schema entry from `components.schemas` or inline.

    `raw` is the source dict — schemas-generator reads it directly. We only
    extract fields that the slicer / naming layer needs to know upfront.
    """
    name: str
    raw: dict[str, Any]


@dataclass(slots=True)
class IROperation:
    """One HTTP operation."""
    operation_id: str
    method: str                       # "get" / "post" / …
    path: str                         # "/api/fleets/{fleet_id}"
    tag: str                          # primary tag (first one)
    summary: str = ""
    parameters: list[dict[str, Any]] = field(default_factory=list)
    request_body_schema_ref: str | None = None  # e.g. "FleetCreate"
    response_schema_ref: str | None = None       # 200/201 ref, or None


@dataclass(slots=True)
class IR:
    schemas: dict[str, IRSchema] = field(default_factory=dict)
    operations: list[IROperation] = field(default_factory=list)


def build_ir(spec: dict[str, Any]) -> IR:
    """Walk a (sliced) OpenAPI spec and emit IR."""
    ir = IR()

    schemas = spec.get("components", {}).get("schemas", {})
    for name, raw in schemas.items():
        if isinstance(raw, dict):
            ir.schemas[name] = IRSchema(name=name, raw=raw)

    paths = spec.get("paths", {})
    for path, item in paths.items():
        if not isinstance(item, dict):
            continue
        for method, op in item.items():
            if method.lower() not in _HTTP_METHODS or not isinstance(op, dict):
                continue
            tags = op.get("tags") or []
            tag = tags[0] if tags else "default"
            ir.operations.append(
                IROperation(
                    operation_id=op.get("operationId") or _fallback_op_id(method, path),
                    method=method.lower(),
                    path=path,
                    tag=tag,
                    summary=op.get("summary", ""),
                    parameters=list(op.get("parameters") or []),
                    request_body_schema_ref=_extract_ref(op.get("requestBody")),
                    response_schema_ref=_extract_response_ref(op.get("responses")),
                )
            )
    return ir


def _extract_ref(body: Any) -> str | None:
    if not isinstance(body, dict):
        return None
    content = body.get("content") or {}
    json_part = content.get("application/json") or {}
    schema = json_part.get("schema") or {}
    return _ref_name(schema.get("$ref"))


def _extract_response_ref(responses: Any) -> str | None:
    if not isinstance(responses, dict):
        return None
    for code in ("200", "201", "202"):
        resp = responses.get(code)
        if isinstance(resp, dict):
            ref = _extract_ref(resp)
            if ref:
                return ref
    return None


def _ref_name(ref: Any) -> str | None:
    if not isinstance(ref, str):
        return None
    prefix = "#/components/schemas/"
    if ref.startswith(prefix):
        return ref[len(prefix):]
    return None


def _fallback_op_id(method: str, path: str) -> str:
    cleaned = path.strip("/").replace("/", "_").replace("{", "").replace("}", "")
    return f"{method}_{cleaned}" if cleaned else method
