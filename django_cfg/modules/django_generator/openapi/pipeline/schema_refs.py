"""Normalize inline OpenAPI request/response schemas before code generation."""

from __future__ import annotations

import logging
from typing import Any

log = logging.getLogger(__name__)
_HTTP_METHODS = {"get", "put", "post", "delete", "patch"}


def promote_inline_schemas(spec: dict[str, Any]) -> dict[str, Any]:
    """Promote inline JSON request/response schemas to named components."""
    for path, item in (spec.get("paths") or {}).items():
        if not isinstance(item, dict):
            continue
        for method, operation in item.items():
            if method.lower() not in _HTTP_METHODS or not isinstance(operation, dict):
                continue
            operation_id = operation.get("operationId") or _fallback_operation_id(method, path)
            responses = operation.get("responses")
            if isinstance(responses, dict):
                for code in ("200", "201", "202"):
                    response = responses.get(code)
                    if isinstance(response, dict):
                        _promote_body(response, spec, operation_id, f"response_{code}")
            request_body = operation.get("requestBody")
            if isinstance(request_body, dict):
                _promote_body(request_body, spec, operation_id, "requestBody")
    return spec


def _promote_body(body: dict[str, Any], spec: dict[str, Any], operation_id: str, kind: str) -> None:
    content = body.get("content") or {}
    json_part = content.get("application/json") or {}
    schema = json_part.get("schema") or {}
    if not schema or "$ref" in schema:
        return
    schemas = spec.setdefault("components", {}).setdefault("schemas", {})
    base = _auto_name(operation_id, kind)
    candidate = base
    counter = 2
    while candidate in schemas:
        candidate = f"{base}_{counter}"
        counter += 1
    schemas[candidate] = schema
    json_part["schema"] = {"$ref": f"#/components/schemas/{candidate}"}
    log.info("Promoted inline schema to %r (%s of %r).", candidate, kind, operation_id)


def _auto_name(operation_id: str, kind: str) -> str:
    base = operation_id
    for suffix in ("_create", "_list", "_retrieve", "_update", "_partial_update", "_destroy"):
        if base.endswith(suffix):
            base = base[: -len(suffix)]
            break
    return f"{base}_{kind}_AutoRef"


def _fallback_operation_id(method: str, path: str) -> str:
    cleaned = path.strip("/").replace("/", "_").replace("{", "").replace("}", "")
    return f"{method}_{cleaned}" if cleaned else method


__all__ = ["promote_inline_schemas"]
