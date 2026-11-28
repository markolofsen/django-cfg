"""Validate before evaluating the projected, scoped QuerySet."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING
from django.db.models import Model, Field

if TYPE_CHECKING:
    from django_cfg.modules.django_mcp.__cfg__ import ModelMCPConfig
    from django_cfg.modules.django_mcp.services.context import MCPContext
import math

from .config import LOOKUPS, MAX_BYTES, MAX_FILTERS, MAX_IN, MAX_OFFSET, MAX_ROWS, MAX_TEXT, ReadPolicyError, ScalarReadPolicy
from django_cfg.modules.django_mcp.tools.results import ToolResult
from .fields import projected_fields, serialize_projected


def scalar(value: object) -> bool:
    return value is None or isinstance(value, (bool, int)) or isinstance(value, float) and math.isfinite(value) or isinstance(value, str) and len(value) <= MAX_TEXT


def checked_filters(raw: object, policy: ScalarReadPolicy, columns: dict[str, Field]) -> dict[str, object]:
    if not isinstance(raw, dict) or len(raw) > MAX_FILTERS:
        raise ReadPolicyError("Use bounded scalar filter arguments.")
    result = {}
    primary = next(name for name, field in columns.items() if field.primary_key)
    for key, value in raw.items():
        parts = key.split("__") if isinstance(key, str) else []
        if not 1 <= len(parts) <= 2:
            raise ReadPolicyError()
        name, lookup = parts[0], parts[1] if len(parts) == 2 else "exact"
        name = primary if name == "pk" else name
        if name not in policy.filter_fields or lookup not in LOOKUPS:
            raise ReadPolicyError()
        if lookup == "in":
            valid = isinstance(value, list) and 0 < len(value) <= MAX_IN and all(scalar(v) for v in value)
        else:
            valid = isinstance(value, bool) if lookup == "isnull" else scalar(value)
        if not valid:
            raise ReadPolicyError()
        if name in policy.scope and (lookup != "exact" or type(value) is not type(policy.scope[name]) or value != policy.scope[name]):
            raise ReadPolicyError("A caller predicate conflicts with the fixed read scope.")
        result[f"{columns[name].attname}__{lookup}"] = value
    return result


def read_model(model: type[Model], grant: ModelMCPConfig, arguments: dict[str, object], *, retrieve: bool = False) -> str:
    if len(json.dumps(arguments, allow_nan=False).encode("utf-8")) > MAX_BYTES:
        raise ReadPolicyError("Model read arguments exceed the byte limit.")
    policy = grant.read_policy
    if policy is None:
        raise ReadPolicyError()
    columns = projected_fields(model, grant)
    primary = next(name for name, field in columns.items() if field.primary_key)
    permitted = {"app_label", "model_name", "pk"} if retrieve else {"app_label", "model_name", "filters", "order_by", "limit", "offset"}
    if set(arguments) - permitted:
        raise ReadPolicyError("Unknown model-read argument.")
    raw: object = arguments.get("filters", {})
    if retrieve:
        identity = arguments.get("pk")
        if isinstance(identity, bool) or not isinstance(identity, (int, str)):
            raise ReadPolicyError()
        raw = {"pk": identity}
    filters = checked_filters(raw, policy, columns)
    limit = 1 if retrieve else arguments.get("limit", grant.max_results)
    offset = 0 if retrieve else arguments.get("offset", 0)
    if type(limit) is not int or limit < 1 or type(offset) is not int or not 0 <= offset <= MAX_OFFSET:
        raise ReadPolicyError("Use positive bounded pagination.")
    order = [] if retrieve else arguments.get("order_by", [])
    if not isinstance(order, list) or len(order) > MAX_FILTERS:
        raise ReadPolicyError()
    ordering = []
    for item in order:
        if not isinstance(item, str) or item.lstrip("-") not in policy.order_fields or item.startswith("--"):
            raise ReadPolicyError()
        name = item.removeprefix("-")
        ordering.append(("-" if item.startswith("-") else "") + columns[name].attname)
    if not any(item.removeprefix("-") == columns[primary].attname for item in ordering):
        ordering.append(columns[primary].attname)
    fixed = {columns[name].attname: value for name, value in policy.scope.items()}
    qs = model._default_manager.filter(**fixed).filter(**filters).values(*(f.attname for f in columns.values())).order_by(*ordering)
    rows = serialize_projected(qs[offset:offset + min(limit, grant.max_results, MAX_ROWS)], columns)
    if retrieve:
        if not rows:
            raise ReadPolicyError("No record matched the approved read scope.")
        payload = rows[0]
    else:
        payload = {"count": len(rows), "model": model._meta.label, "results": rows}
    text = json.dumps(payload, allow_nan=False)
    if len(text.encode("utf-8")) > MAX_BYTES:
        raise ReadPolicyError("The projected model response exceeds the byte limit.")
    return text


def policy_read(context: MCPContext, arguments: object, *, retrieve: bool = False) -> str | ToolResult | None:
    """None selects the unchanged legacy reader; a projection never falls back after refusal."""
    from django.apps import apps

    if not isinstance(arguments, dict):
        return ToolResult("Invalid model read arguments.", is_error=True)
    restricted = getattr(getattr(context, "profile", None), "restricted_reads", False)
    app, name = arguments.get("app_label"), arguments.get("model_name")
    if not isinstance(app, str) or not isinstance(name, str):
        return ToolResult("Invalid model read arguments.", is_error=True) if restricted else None
    grant = context.config.get_model_config(app, name)
    if grant is None or grant.read_policy is None:
        return ToolResult("Model is not approved for scalar reads.", is_error=True) if restricted else None
    operation = "retrieve" if retrieve else "list"
    try:
        if not context.config.is_model_exposed(app, name) or operation not in grant.allowed_operations:
            raise ReadPolicyError()
        return read_model(apps.get_model(app, name), grant, arguments, retrieve=retrieve)
    except ReadPolicyError as exc:
        return ToolResult(str(exc), is_error=True)
    except Exception:
        return ToolResult("The approved scalar model read could not complete.", is_error=True)
