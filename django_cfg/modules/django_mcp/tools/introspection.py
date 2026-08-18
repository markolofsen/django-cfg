"""Introspection Tools for MCP."""

import json
from typing import Any, Dict

from django.apps import apps
from django.urls import get_resolver

from django_cfg.modules.django_mcp.tools.base import MCPTool
from django_cfg.modules.django_mcp.services.context import MCPContext


#: Fallback field list, used only when the object is not a pydantic model.
#:
#: The model path below copies *every* declared field instead, because naming
#: them here is exactly how ``max_depth`` would go missing the day someone
#: reads it: the readers use ``intro.get(flag, False)``, so a dropped key is
#: indistinguishable from a flag deliberately turned off.
_INTROSPECTION_FLAGS = ("enabled", "expose_urls", "expose_code", "max_depth")


def _get_introspection_config(context: MCPContext) -> Dict[str, Any]:
    """Safe accessor for introspection config (handles dict or model).

    Every declared flag is copied out, not just ``enabled``. Projecting a model
    down to ``{"enabled": ...}`` made ``expose_urls`` and ``expose_code``
    unreachable: the callers read them with ``.get(flag, False)``, so a config
    that plainly said ``expose_urls=True`` produced "URL exposure is not
    enabled" on every call, and the operator's own setting could not be
    reconciled with the tool's answer without reading this function.

    That is the expensive shape of bug — the feature is configured, the config
    object is correct, and only an invisible projection in between disagrees.
    """
    config = context.config
    intro = config.get("introspection", {}) if isinstance(config, dict) else config.introspection

    if isinstance(intro, dict):
        return intro

    dump = getattr(intro, "model_dump", None)
    if callable(dump):
        # Ask the model for everything it declares, so a field added later
        # arrives here without anyone remembering to update a list.
        dumped = dump()
        if isinstance(dumped, dict):
            return dumped
    return {flag: getattr(intro, flag, False) for flag in _INTROSPECTION_FLAGS}


def _as_int(value: Any, default: int) -> int:
    """Coerce an LLM-supplied argument to an int, falling back on nonsense.

    Arguments here are written by a model, so a string where an integer belongs
    is routine rather than exceptional — and refusing the whole call over one
    malformed field costs the caller a round trip to learn nothing.
    """
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


class ListAppsTool(MCPTool):
    """List all installed Django apps and their models."""

    name = "list_apps"
    description = "List all installed Django applications and their models. Use this to discover the application structure."
    input_schema = {
        "type": "object",
        "properties": {
            "include_models": {
                "type": "boolean",
                "description": "Whether to include model details for each app",
                "default": False,
            }
        },
    }

    def execute(self, context: MCPContext, arguments: Dict[str, Any]) -> str:
        """Execute the list_apps tool."""
        intro = _get_introspection_config(context)
        if not intro.get("enabled", False):
            return "Error: Introspection is not enabled"

        include_models = arguments.get("include_models", False)
        result = []

        for app_config in apps.get_app_configs():
            app_info = {
                "name": app_config.name,
                "label": app_config.label,
                "path": str(app_config.path),
            }

            if include_models:
                models = []
                for model in app_config.get_models():
                    # Only expose if configured in MCP config
                    if context.config.is_model_exposed(
                        app_config.label, model.__name__
                    ):
                        models.append({
                            "name": model.__name__,
                            "verbose_name": str(model._meta.verbose_name),
                        })
                app_info["models"] = models

            result.append(app_info)

        return json.dumps(result, indent=2)


class GetModelSchemaTool(MCPTool):
    """Get detailed schema for a Django model."""

    name = "get_model_schema"
    description = "Get detailed schema for a specific Django model including fields, relationships, and constraints."
    input_schema = {
        "type": "object",
        "properties": {
            "app_label": {
                "type": "string",
                "description": "Django app label (e.g., 'accounts', 'auth')",
            },
            "model_name": {
                "type": "string",
                "description": "Model class name (e.g., 'User', 'Group')",
            }
        },
        "required": ["app_label", "model_name"],
    }

    def execute(self, context: MCPContext, arguments: Dict[str, Any]) -> str:
        """Execute the get_model_schema tool."""
        app_label = arguments.get("app_label")
        model_name = arguments.get("model_name")

        if not app_label or not model_name:
            return "Error: app_label and model_name are required"

        # Check if model is exposed
        if not context.config.is_model_exposed(app_label, model_name):
            return f"Error: Model '{app_label}.{model_name}' is not exposed to MCP"

        # Get model
        try:
            model = apps.get_model(app_label, model_name)
        except LookupError:
            return f"Error: Model '{app_label}.{model_name}' not found"

        # Build schema
        schema = {
            "app": app_label,
            "model": model_name,
            "verbose_name": str(model._meta.verbose_name),
            "verbose_name_plural": str(model._meta.verbose_name_plural),
            "fields": [],
            "relationships": [],
        }

        model_config = context.config.get_model_config(app_label, model_name)
        hidden_fields = model_config.hidden_fields if model_config else []

        for field in model._meta.fields:
            if field.name in hidden_fields:
                continue

            field_info = {
                "name": field.name,
                "type": field.get_internal_type(),
                "nullable": field.null,
                "blank": field.blank,
                "primary_key": field.primary_key,
                "unique": field.unique,
            }

            if hasattr(field, "max_length") and field.max_length:
                field_info["max_length"] = field.max_length

            if field.choices:
                field_info["choices"] = [
                    {"value": c[0], "label": c[1]}
                    for c in field.choices
                ]

            if field.help_text:
                field_info["help_text"] = str(field.help_text)

            schema["fields"].append(field_info)

        # Add relationships (ForeignKey, ManyToMany, OneToOne)
        for field in model._meta.fields + model._meta.many_to_many:
            if field.is_relation and field.name not in hidden_fields:
                rel_info = {
                    "name": field.name,
                    "type": field.get_internal_type(),
                    "related_model": f"{field.related_model._meta.app_label}.{field.related_model._meta.model_name}",
                }
                schema["relationships"].append(rel_info)

        return json.dumps(schema, indent=2)


class ListURLsTool(MCPTool):
    """List URL patterns registered in Django."""

    #: Cap the response so one call cannot consume the caller's whole context.
    #:
    #: Measured on a real project: the unbounded form returned 9,681 patterns —
    #: 364 KB, roughly 91k tokens — in a single answer. An agent that spends its
    #: entire window listing URLs has nothing left to do the task it was listing
    #: them for, and the tool looks like it "worked".
    DEFAULT_LIMIT = 200
    MAX_LIMIT = 2000

    name = "list_urls"
    description = (
        "List URL patterns registered in Django. Only available when introspection "
        "is enabled. Results are capped, and a large project has thousands — pass "
        "`contains` to filter to the prefix you care about (e.g. 'apix/billing') "
        "rather than paging through everything."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "contains": {
                "type": "string",
                "description": "Only patterns whose path or name contains this substring.",
            },
            "limit": {
                "type": "integer",
                "description": f"Max patterns to return (default {DEFAULT_LIMIT}, max {MAX_LIMIT}).",
            },
            "offset": {
                "type": "integer",
                "description": "Skip this many matches — for paging through a filtered set.",
            },
        },
    }

    def execute(self, context: MCPContext, arguments: Dict[str, Any]) -> str:
        """Execute the list_urls tool."""
        intro = _get_introspection_config(context)
        if not intro.get("enabled", False):
            return "Error: Introspection is not enabled"

        if not intro.get("expose_urls", False):
            return "Error: URL exposure is not enabled"

        resolver = get_resolver()
        urls = self._extract_urls(resolver.url_patterns)
        total = len(urls)

        needle = (arguments.get("contains") or "").strip().lower()
        if needle:
            urls = [
                u for u in urls
                if needle in u["pattern"].lower() or needle in (u["name"] or "").lower()
            ]
        matched = len(urls)

        # `is None`, not a falsy test: `limit=0` is a value the caller passed,
        # and `or DEFAULT_LIMIT` would silently turn it into 200 — the tool
        # answering a question nobody asked, which is how a caller decides it
        # is being ignored.
        limit = _as_int(arguments.get("limit"), self.DEFAULT_LIMIT)
        limit = max(1, min(limit, self.MAX_LIMIT))

        offset = max(0, _as_int(arguments.get("offset"), 0))

        page = urls[offset:offset + limit]

        # Report the truncation in the payload. A silently capped list reads as
        # "these are all the URLs", which is how somebody concludes a route was
        # never deployed when it was merely past the cap.
        return json.dumps(
            {
                "total_urls": total,
                "matched": matched,
                "returned": len(page),
                "offset": offset,
                "truncated": offset + len(page) < matched,
                "filter": needle or None,
                "urls": page,
            },
            indent=2,
        )

    def _extract_urls(self, patterns, prefix: str = "") -> list:
        """Recursively extract URL patterns."""
        urls = []
        for pattern in patterns:
            if hasattr(pattern, "url_patterns"):
                # Include URL resolver (e.g., include())
                sub_urls = self._extract_urls(
                    pattern.url_patterns,
                    prefix + str(pattern.pattern),
                )
                urls.extend(sub_urls)
            elif hasattr(pattern, "name") and pattern.name:
                urls.append({
                    "pattern": prefix + str(pattern.pattern),
                    "name": pattern.name,
                    "view": pattern.lookup_str if hasattr(pattern, "lookup_str") else str(pattern.callback),
                })
        return urls


# Tool instances for registry
list_apps_tool = ListAppsTool()
get_model_schema_tool = GetModelSchemaTool()
list_urls_tool = ListURLsTool()
