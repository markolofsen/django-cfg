"""Minimal IR over an OpenAPI 3.1 spec.

The spec produced by FastAPI + sliced by `core.slicer` is what we operate on.
We don't try to be a full OpenAPI parser — only what zod/hooks generators
need. Everything else stays as raw dict in `.raw`.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Literal

_log = logging.getLogger(__name__)

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
class IRParam:
    """One path or query parameter extracted from an OpenAPI `parameters` entry."""
    name: str
    location: Literal["path", "query"]  # "in": "path" | "query"
    required: bool
    schema: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class IROperation:
    """One HTTP operation."""
    operation_id: str
    method: str                       # "get" / "post" / …
    path: str                         # "/api/fleets/{fleet_id}"
    tag: str                          # primary tag (first one)
    summary: str = ""
    path_params: list[IRParam] = field(default_factory=list)
    query_params: list[IRParam] = field(default_factory=list)
    parameters: list[dict[str, Any]] = field(default_factory=list)  # raw, for compat
    request_body_schema_ref: str | None = None  # e.g. "FleetCreate"
    response_schema_ref: str | None = None       # 200/201 ref, or None
    is_paginated: bool = False        # True when response_schema_ref starts with "Paginated"


@dataclass(slots=True)
class IR:
    schemas: dict[str, IRSchema] = field(default_factory=dict)
    operations: list[IROperation] = field(default_factory=list)


def promote_inline_schemas(spec: dict[str, Any]) -> dict[str, Any]:
    """Promote every inline response / requestBody schema to a named $ref.

    Mutates *spec* in-place (adds entries to ``components.schemas`` and
    replaces inline dicts with ``{"$ref": "#/components/schemas/..."}``).
    Safe to call multiple times — already-promoted schemas are left untouched.
    """
    paths = spec.get("paths", {})
    for path, item in paths.items():
        if not isinstance(item, dict):
            continue
        for method, op in item.items():
            if method.lower() not in _HTTP_METHODS or not isinstance(op, dict):
                continue
            op_id = op.get("operationId") or _fallback_op_id(method, path)

            # responses
            responses = op.get("responses")
            if isinstance(responses, dict):
                for code in ("200", "201", "202"):
                    resp = responses.get(code)
                    if isinstance(resp, dict):
                        _extract_ref(
                            resp,
                            op_id=op_id,
                            kind=f"response_{code}",
                            spec=spec,
                        )

            # requestBody
            body = op.get("requestBody")
            if isinstance(body, dict):
                _extract_ref(
                    body,
                    op_id=op_id,
                    kind="requestBody",
                    spec=spec,
                )

    return spec


def build_ir(spec: dict[str, Any]) -> IR:
    """Walk a (sliced) OpenAPI spec and emit IR."""
    ir = IR()

    schemas = spec.get("components", {}).get("schemas", {})
    for name, raw in schemas.items():
        if isinstance(raw, dict):
            ir.schemas[name] = IRSchema(name=name, raw=raw)

    seen_ids: dict[str, str] = {}  # operation_id → first path

    paths = spec.get("paths", {})
    for path, item in paths.items():
        if not isinstance(item, dict):
            continue
        for method, op in item.items():
            if method.lower() not in _HTTP_METHODS or not isinstance(op, dict):
                continue
            tags = op.get("tags") or []
            if not tags:
                op_id = op.get("operationId") or f"{method.upper()} {path}"
                raise ValueError(
                    f"Endpoint has no tag: {method.upper()} {path} "
                    f"(operationId={op_id!r}). "
                    f"Add a tag to every operation before running the generator."
                )
            tag = tags[0]
            operation_id = op.get("operationId") or _fallback_op_id(method, path)

            if operation_id in seen_ids:
                raise ValueError(
                    f"Duplicate operationId {operation_id!r}: "
                    f"first seen at {seen_ids[operation_id]!r}, "
                    f"also at {path!r}."
                )
            seen_ids[operation_id] = path

            if method.lower() == "delete" and op.get("requestBody"):
                raise ValueError(
                    f"DELETE operation {operation_id!r} at {path!r} has a requestBody. "
                    f"Django REST Framework does not support request bodies on DELETE. "
                    f"Remove the body or suppress the schema with "
                    f"@extend_schema(request=None) on the view."
                )

            raw_params: list[dict[str, Any]] = list(op.get("parameters") or [])
            path_params, query_params = _parse_params(raw_params)

            response_ref = _extract_response_ref(
                op.get("responses"),
                op_id=op.get("operationId") or f"{method.upper()} {path}",
            )
            ir.operations.append(
                IROperation(
                    operation_id=operation_id,
                    method=method.lower(),
                    path=path,
                    tag=tag,
                    summary=op.get("summary", ""),
                    path_params=path_params,
                    query_params=query_params,
                    parameters=raw_params,
                    request_body_schema_ref=_extract_ref(
                        op.get("requestBody"),
                        op_id=op.get("operationId") or f"{method.upper()} {path}",
                        kind="requestBody",
                    ),
                    response_schema_ref=response_ref,
                    is_paginated=isinstance(response_ref, str) and response_ref.startswith("Paginated"),
                )
            )

    for oper in ir.operations:
        for ref_name, kind in (
            (oper.request_body_schema_ref, "requestBody"),
            (oper.response_schema_ref, "response"),
        ):
            if ref_name is not None and ref_name not in ir.schemas:
                _log.warning(
                    "Dangling $ref %r (%s of %r) — schema not found in components.schemas. "
                    "Hey API will still use it but zod generation will be skipped.",
                    ref_name, kind, oper.operation_id,
                )

    return ir


def _parse_params(params: list[dict[str, Any]]) -> tuple[list[IRParam], list[IRParam]]:
    """Split raw OpenAPI parameters into (path_params, query_params)."""
    path: list[IRParam] = []
    query: list[IRParam] = []
    for p in params:
        if not isinstance(p, dict):
            continue
        location = p.get("in", "")
        if location not in ("path", "query"):
            continue
        name = p.get("name", "")
        if not name:
            continue
        schema = p.get("schema") or {}
        required = bool(p.get("required", location == "path"))
        param = IRParam(name=name, location=location, required=required, schema=schema)
        if location == "path":
            path.append(param)
        else:
            query.append(param)
    return path, query


def _ensure_components_schemas(spec: dict[str, Any]) -> dict[str, Any]:
    """Return (and create if missing) the components.schemas dict."""
    components = spec.setdefault("components", {})
    return components.setdefault("schemas", {})


def _auto_name(op_id: str, kind: str) -> str:
    """Generate a collision-resistant schema name from operationId + kind."""
    base = op_id
    for suffix in ("_create", "_list", "_retrieve", "_update", "_partial_update", "_destroy"):
        if base.endswith(suffix):
            base = base[: -len(suffix)]
            break
    return f"{base}_{kind}_AutoRef"


def _extract_ref(
    body: Any,
    *,
    op_id: str = "",
    kind: str = "",
    spec: dict[str, Any] | None = None,
) -> str | None:
    if not isinstance(body, dict):
        return None
    content = body.get("content") or {}
    json_part = content.get("application/json") or {}
    schema = json_part.get("schema") or {}
    if not schema:
        return None
    ref = _ref_name(schema.get("$ref"))
    if ref is None and schema:
        if spec is not None:
            schemas = _ensure_components_schemas(spec)
            auto_name = _auto_name(op_id, kind)
            # collision guard — append _2, _3, …
            candidate = auto_name
            counter = 2
            while candidate in schemas:
                candidate = f"{auto_name}_{counter}"
                counter += 1
            schemas[candidate] = schema
            # mutate inline → $ref so downstream tools see a normal ref
            json_part["schema"] = {"$ref": f"#/components/schemas/{candidate}"}
            _log.info(
                "Promoted inline schema to $ref %r (%s of %r).",
                candidate,
                kind or "body",
                op_id,
            )
            return candidate
        else:
            _log.warning(
                "Inline schema (no $ref) on %s of %r — schema will be ignored by ts_extras. "
                "Use a named component ($ref) to enable zod validation and typed hooks.",
                kind or "body",
                op_id,
            )
    return ref


def _extract_response_ref(
    responses: Any,
    *,
    op_id: str = "",
    spec: dict[str, Any] | None = None,
) -> str | None:
    if not isinstance(responses, dict):
        return None
    for code in ("200", "201", "202"):
        resp = responses.get(code)
        if isinstance(resp, dict):
            ref = _extract_ref(resp, op_id=op_id, kind=f"response_{code}", spec=spec)
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
