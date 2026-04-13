"""Introspection Tools for MCP."""

import json
from typing import Any, Dict

from django.apps import apps
from django.urls import get_resolver

from django_cfg.modules.django_mcp.tools.base import MCPTool
from django_cfg.modules.django_mcp.services.context import MCPContext


def _get_introspection_config(context: MCPContext):
    """Safe accessor for introspection config (handles dict or model)."""
    config = context.config
    if isinstance(config, dict):
        intro = config.get("introspection", {})
        return intro if isinstance(intro, dict) else {"enabled": getattr(intro, "enabled", False)}
    else:
        intro = config.introspection
        if isinstance(intro, dict):
            return intro
        return {"enabled": getattr(intro, "enabled", False)}


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

    name = "list_urls"
    description = "List URL patterns registered in Django. Only available when introspection is enabled."
    input_schema = {
        "type": "object",
        "properties": {},
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

        return json.dumps(urls, indent=2)

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
