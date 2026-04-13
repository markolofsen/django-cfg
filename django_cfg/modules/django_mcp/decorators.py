"""Decorators for MCP Tool Registration."""

import json
from functools import wraps
from typing import Any, Callable, Dict, List, Optional

from django_cfg.modules.django_mcp.tools.base import MCPTool, tool_registry
from django_cfg.modules.django_mcp.services.context import MCPContext


def mcp_viewset(
    operations: Optional[List[str]] = None,
    name_prefix: Optional[str] = None,
):
    """
    Decorator to expose a DRF ViewSet as MCP tools.

    Usage:
        @mcp_viewset(operations=['list', 'retrieve'])
        class MyModelViewSet(ModelViewSet):
            ...

    This automatically creates MCP tools for the specified operations.
    """
    operations = operations or ["list", "retrieve"]

    def decorator(viewset_cls):
        # Extract model from ViewSet
        model = getattr(viewset_cls, "model", None)
        if not model:
            serializer_class = getattr(viewset_cls, "serializer_class", None)
            if serializer_class:
                model = getattr(serializer_class.Meta, "model", None)

        if not model:
            raise ValueError(f"ViewSet {viewset_cls.__name__} has no model or serializer")

        app_label = model._meta.app_label
        model_name = model._meta.model_name
        tool_prefix = name_prefix or f"{app_label}_{model_name}"

        # Create tools for each operation
        if "list" in operations:
            class ListTool(MCPTool):
                name = f"{tool_prefix}_list"
                description = f"List {model._meta.verbose_name_plural}"
                input_schema = {
                    "type": "object",
                    "properties": {
                        "limit": {"type": "integer", "default": 100},
                        "offset": {"type": "integer", "default": 0},
                    },
                }

                def execute(self, context: MCPContext, arguments: Dict[str, Any]) -> str:
                    qs = model.objects.all()
                    limit = min(arguments.get("limit", 100), 100)
                    offset = arguments.get("offset", 0)
                    results = list(qs[offset:offset + limit].values())
                    return json.dumps({"count": len(results), "results": results}, default=str)

            tool_registry.register(ListTool())

        if "retrieve" in operations:
            class RetrieveTool(MCPTool):
                name = f"{tool_prefix}_retrieve"
                description = f"Get a single {model._meta.verbose_name}"
                input_schema = {
                    "type": "object",
                    "properties": {
                        "pk": {"type": "integer", "description": "Primary key"},
                    },
                    "required": ["pk"],
                }

                def execute(self, context: MCPContext, arguments: Dict[str, Any]) -> str:
                    pk = arguments.get("pk")
                    try:
                        obj = model.objects.get(pk=pk)
                        return json.dumps({
                            field.name: getattr(obj, field.name)
                            for field in model._meta.fields
                        }, default=str)
                    except model.DoesNotExist:
                        return f"Not found"

            tool_registry.register(RetrieveTool())

        if "create" in operations:
            class CreateTool(MCPTool):
                name = f"{tool_prefix}_create"
                description = f"Create a new {model._meta.verbose_name}"
                input_schema = {
                    "type": "object",
                    "properties": {
                        "data": {
                            "type": "object",
                            "description": "Object data to create",
                        },
                    },
                    "required": ["data"],
                }

                def execute(self, context: MCPContext, arguments: Dict[str, Any]) -> str:
                    data = arguments.get("data", {})
                    try:
                        obj = model.objects.create(**data)
                        return json.dumps({"id": obj.pk, "created": True}, default=str)
                    except Exception as e:
                        return f"Error creating object: {str(e)}"

            tool_registry.register(CreateTool())

        return viewset_cls

    return decorator


def mcp_tool(name: str, description: str, input_schema: Dict[str, Any]):
    """
    Decorator to expose a function as an MCP tool.

    Usage:
        @mcp_tool(
            name="calculate_revenue",
            description="Calculate revenue for a period",
            input_schema={
                "type": "object",
                "properties": {
                    "start_date": {"type": "string"},
                    "end_date": {"type": "string"},
                },
                "required": ["start_date", "end_date"],
            }
        )
        def calculate_revenue(ctx: MCPContext, start_date: str, end_date: str) -> str:
            # Implementation
            return "Revenue: $1000"
    """
    def decorator(func: Callable):
        class DecoratedTool(MCPTool):
            def __init__(self):
                self.name = name
                self.description = description
                self.input_schema = input_schema
                self.func = func

            def execute(self, context: MCPContext, arguments: Dict[str, Any]) -> str:
                return self.func(context, **arguments)

        tool_registry.register(DecoratedTool())

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator
