"""MCP Server Info View — single endpoint returning server + tools info."""

import logging
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from django_cfg.modules.django_mcp.handlers.tools import tool_registry

logger = logging.getLogger(__name__)


class MCPInfoView(APIView):
    """
    GET /cfg/mcp/info/

    Returns server metadata and all available tools in one request.
    Faster than JSON-RPC initialize + tools/list (single HTTP GET).

    Response:
    {
        "server": {
            "name": "django-cfg-mcp",
            "version": "1.0.0",
            "protocol": "2025-03-26",
            "description": "..."
        },
        "tools": [
            {
                "name": "get_billing_plans",
                "description": "...",
                "input_schema": {...}
            }
        ],
        "total_tools": 24
    }
    """
    permission_classes = [AllowAny]

    def get(self, request):
        from django_cfg.core.state import get_current_config
        config = get_current_config()
        mcp_config = config.mcp if config and config.mcp else None

        server_info = {
            "name": "django-cfg-mcp",
            "version": "1.0.0",
            "protocol": "2025-03-26",
            "description": (
                "Django-CFG MCP server — AI agents can query models, "
                "execute commands, and introspect the application."
            ),
        }

        if mcp_config:
            server_info["introspection_enabled"] = getattr(
                mcp_config.introspection if hasattr(mcp_config, 'introspection') else {},
                'enabled', False
            )
            server_info["llm_model"] = getattr(mcp_config, 'llm_model', 'openai/gpt-4.1-nano')

        tools = []
        for tool in tool_registry.get_all_tools(None):
            tools.append({
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.input_schema,
            })

        return JsonResponse({
            "server": server_info,
            "tools": tools,
            "total_tools": len(tools),
        })
