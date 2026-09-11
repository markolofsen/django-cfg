# MCP Project Tools

Add your custom MCP tools here. Files in this directory are auto-discovered at Django startup.

## Quick Start

1. Create a Python file in this directory: `mcp/tools/my_tool.py`
2. Define your tool class extending `MCPTool`
3. Register it with `tool_registry.register(MyTool())`

## Example

```python
# mcp/tools/orders.py
from django_cfg.modules.django_mcp.tools.base import MCPTool, tool_registry


class GetRecentOrdersTool(MCPTool):
    name = "get_recent_orders"
    description = "Get the most recent orders for a user"
    input_schema = {
        "type": "object",
        "properties": {
            "user_id": {"type": "integer", "description": "User ID"},
            "limit": {"type": "integer", "default": 10, "description": "Number of orders"},
        },
        "required": ["user_id"],
    }

    def execute(self, context, arguments):
        from orders.models import Order
        orders = Order.objects.filter(
            user_id=arguments["user_id"]
        ).order_by("-created_at")[:arguments.get("limit", 10)]
        
        return f"Found {orders.count()} recent orders"


# Register the tool
tool_registry.register(GetRecentOrdersTool())
```

## Available Context

The `context` parameter provides:
- `context.config` — MCP configuration
- `context.user` — Authenticated user (or AnonymousUser)
- `context.session_key` — Session identifier
- `context.request` — HTTP request object

## Naming Conventions

- Use `snake_case` for tool names
- Tool names should be unique across all registered tools
- Description should be clear and concise (shown to AI agents)

## Security

- Tools execute with the same permissions as the authenticated user
- Validate all input arguments
- Don't expose sensitive data in tool outputs
- Use `context.config.redaction` settings for automatic PII redaction
