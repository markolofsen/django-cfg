"""Model Query and Manipulation Tools for MCP."""

import json
from typing import Any, Dict, List
from django.core.exceptions import ValidationError
from django.db import models

from django_cfg.modules.django_mcp.tools.base import MCPTool
from django_cfg.modules.django_mcp.services.context import MCPContext
from django_cfg.modules.django_mcp.services.redactor import apply_redaction, RedactionMode


class QueryModelTool(MCPTool):
    """Query a Django model with filters."""

    name = "query_model"
    description = "Query a Django model with filters. Returns a list of matching records."
    input_schema = {
        "type": "object",
        "properties": {
            "app_label": {"type": "string", "description": "App label (e.g., 'accounts', 'profiles')"},
            "model_name": {"type": "string", "description": "Model name (e.g., 'user', 'userprofile')"},
            "filters": {
                "type": "object",
                "description": "Django ORM filter kwargs (e.g., {'status': 'active'})",
            },
            "limit": {"type": "integer", "description": "Max results (default 100)"},
            "offset": {"type": "integer", "description": "Pagination offset"},
            "order_by": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Fields to order by (prefix with - for descending)",
            },
        },
        "required": ["app_label", "model_name"],
    }

    def execute(self, context: MCPContext, arguments: Dict[str, Any]) -> str:
        """Execute the query_model tool."""
        from django.apps import apps

        app_label = arguments.get("app_label")
        model_name = arguments.get("model_name")

        # Check if model is exposed
        if not context.config.is_model_exposed(app_label, model_name):
            return f"Error: Model '{app_label}.{model_name}' is not exposed to MCP"

        model_config = context.config.get_model_config(app_label, model_name)
        if not model_config:
            return f"Error: Model '{app_label}.{model_name}' configuration not found"

        if "list" not in model_config.allowed_operations:
            return "Error: List operation not allowed for this model"

        # Get model
        try:
            model = apps.get_model(app_label, model_name)
        except LookupError:
            return f"Error: Model '{app_label}.{model_name}' not found"

        # Build queryset
        qs = model.objects.all()

        # Apply filters (validated through Django ORM - prevents injection)
        filters = arguments.get("filters", {})
        try:
            qs = qs.filter(**filters)
        except Exception as e:
            return f"Error: Invalid filters: {e}"

        # Apply ordering
        order_by = arguments.get("order_by")
        if order_by:
            try:
                qs = qs.order_by(*order_by)
            except Exception as e:
                return f"Error: Invalid order_by: {e}"

        # Apply limits
        limit = min(arguments.get("limit", 100), model_config.max_results)
        offset = arguments.get("offset", 0)
        qs = qs[offset:offset + limit]

        # Serialize results
        hidden_fields = model_config.hidden_fields
        results = []
        for obj in qs:
            obj_data = {}
            for field in model._meta.fields:
                if field.name in hidden_fields:
                    continue
                value = getattr(obj, field.name)
                # Convert to JSON-safe type
                if isinstance(value, models.Model):
                    obj_data[field.name] = value.pk if value else None
                elif hasattr(value, "isoformat"):  # datetime
                    obj_data[field.name] = value.isoformat()
                elif hasattr(value, "__iter__") and not isinstance(value, str):
                    obj_data[field.name] = list(value)
                else:
                    obj_data[field.name] = value
            results.append(obj_data)

        # Apply redaction
        mode = RedactionMode(context.config.redaction.mode.lower())
        results = apply_redaction(results, mode)

        return json.dumps({
            "count": len(results),
            "model": f"{app_label}.{model_name}",
            "results": results,
        }, indent=2, default=str)


class GetObjectTool(MCPTool):
    """Get a single object by primary key."""

    name = "get_object"
    description = "Get a single Django model object by its primary key."
    input_schema = {
        "type": "object",
        "properties": {
            "app_label": {"type": "string", "description": "App label"},
            "model_name": {"type": "string", "description": "Model name"},
            "pk": {"type": ["string", "integer"], "description": "Primary key value"},
        },
        "required": ["app_label", "model_name", "pk"],
    }

    def execute(self, context: MCPContext, arguments: Dict[str, Any]) -> str:
        """Execute the get_object tool."""
        from django.apps import apps

        app_label = arguments.get("app_label")
        model_name = arguments.get("model_name")
        pk = arguments.get("pk")

        if not context.config.is_model_exposed(app_label, model_name):
            return f"Error: Model '{app_label}.{model_name}' is not exposed"

        model_config = context.config.get_model_config(app_label, model_name)
        if not model_config:
            return f"Error: Model configuration not found"

        if "retrieve" not in model_config.allowed_operations:
            return "Error: Retrieve operation not allowed"

        try:
            model = apps.get_model(app_label, model_name)
        except LookupError:
            return "Error: Model not found"

        try:
            obj = model.objects.get(pk=pk)
        except model.DoesNotExist:
            return f"Error: Object with pk={pk} not found"

        # Serialize
        hidden_fields = model_config.hidden_fields
        obj_data = {}
        for field in model._meta.fields:
            if field.name in hidden_fields:
                continue
            value = getattr(obj, field.name)
            if isinstance(value, models.Model):
                obj_data[field.name] = value.pk if value else None
            elif hasattr(value, "isoformat"):
                obj_data[field.name] = value.isoformat()
            elif hasattr(value, "__iter__") and not isinstance(value, str):
                obj_data[field.name] = list(value)
            else:
                obj_data[field.name] = value

        # Apply redaction
        mode = RedactionMode(context.config.redaction.mode.lower())
        obj_data = apply_redaction(obj_data, mode)

        return json.dumps(obj_data, indent=2, default=str)


# Create instances for registry
query_model_tool = QueryModelTool()
get_object_tool = GetObjectTool()
