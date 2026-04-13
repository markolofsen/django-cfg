"""MCP Resources Handler."""

from typing import Any, Dict

from django.apps import apps
from django_cfg.modules.django_mcp.services.context import MCPContext
from django_cfg.modules.django_mcp.protocols.types import MCPResourceDefinition
import json


class ResourcesHandler:
    """Handle MCP resources/list and resources/read methods."""

    @staticmethod
    def handle_resources_list(params: Dict[str, Any], context: MCPContext) -> Dict[str, Any]:
        """Return list of available resources."""
        resources = []

        if not context.config.introspection.enabled:
            return {"resources": resources}

        # Expose model schemas as resources
        for app_label, app_config in context.config.exposed_apps.items():
            if not app_config.enabled:
                continue

            for model_name, model_config in app_config.models.items():
                if not model_config.enabled:
                    continue

                uri = f"django://{app_label}/{model_name}/schema"
                resources.append({
                    "uri": uri,
                    "name": f"{app_label}.{model_name} Schema",
                    "description": f"Schema for {app_label}.{model_name}",
                    "mimeType": "application/json",
                })

        return {"resources": resources}

    @staticmethod
    def handle_resources_read(params: Dict[str, Any], context: MCPContext) -> Dict[str, Any]:
        """Read a specific resource by URI."""
        uri = params.get("uri")
        if not uri:
            raise ValueError("Resource URI is required")

        # Parse URI: django://{app_label}/{model_name}/schema
        if not uri.startswith("django://"):
            return {"contents": [], "isError": True}

        path = uri.replace("django://", "")
        parts = path.split("/")
        if len(parts) < 3:
            return {"contents": [], "isError": True}

        app_label = parts[0]
        model_name = parts[1]
        resource_type = parts[2]

        if resource_type != "schema":
            return {"contents": [], "isError": True}

        # Check if model is exposed
        if not context.config.is_model_exposed(app_label, model_name):
            return {"contents": [], "isError": True}

        # Get model
        try:
            model = apps.get_model(app_label, model_name)
        except LookupError:
            return {"contents": [], "isError": True}

        # Build schema
        model_config = context.config.get_model_config(app_label, model_name)
        hidden_fields = model_config.hidden_fields if model_config else []

        schema = {
            "app": app_label,
            "model": model_name,
            "verbose_name": str(model._meta.verbose_name),
            "fields": [],
        }

        for field in model._meta.fields:
            if field.name in hidden_fields:
                continue
            schema["fields"].append({
                "name": field.name,
                "type": field.get_internal_type(),
                "nullable": field.null,
            })

        return {
            "contents": [
                {
                    "uri": uri,
                    "mimeType": "application/json",
                    "text": json.dumps(schema, indent=2),
                }
            ],
        }
