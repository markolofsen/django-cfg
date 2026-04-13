"""MCP Tools Handler."""

from typing import Any, Dict, List

from django_cfg.modules.django_mcp.services.context import MCPContext
from django_cfg.modules.django_mcp.exceptions import MCPPermissionDenied
from django_cfg.modules.django_mcp.tools.introspection import (
    list_apps_tool,
    get_model_schema_tool,
    list_urls_tool,
)
from django_cfg.modules.django_mcp.tools.model_tools import (
    query_model_tool,
    get_object_tool,
)
from django_cfg.modules.django_mcp.tools.command_tool import execute_command_tool
from django_cfg.modules.django_mcp.tools.user_info import get_user_info_tool
from django_cfg.modules.django_mcp.agent.orm_tools import (
    aggregate_model_tool,
    time_series_tool,
    top_values_tool,
    distribution_tool,
)
# Use the GLOBAL registry — do NOT create a new one
from django_cfg.modules.django_mcp.tools.base import tool_registry

# Register introspection tools
tool_registry.register(list_apps_tool)
tool_registry.register(get_model_schema_tool)
tool_registry.register(list_urls_tool)

# Register user info tool (always available)
tool_registry.register(get_user_info_tool)

# Register model query tools
tool_registry.register(query_model_tool)
tool_registry.register(get_object_tool)

# Register command execution tool
tool_registry.register(execute_command_tool)

# Register advanced analytics tools
tool_registry.register(aggregate_model_tool)
tool_registry.register(time_series_tool)
tool_registry.register(top_values_tool)
tool_registry.register(distribution_tool)


class ToolsHandler:
    """Handle MCP tools/list and tools/call methods."""

    @staticmethod
    def handle_tools_list(params: Dict[str, Any], context: MCPContext) -> Dict[str, Any]:
        """Return list of available tools."""
        tools = []
        for tool in tool_registry.get_all_tools(context):
            tools.append(tool.to_definition())

        return {"tools": tools}

    @staticmethod
    def handle_tools_call(params: Dict[str, Any], context: MCPContext) -> Dict[str, Any]:
        """Execute a tool call."""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if not tool_name:
            raise ValueError("Tool name is required")

        # Find and execute tool
        tool = tool_registry.get_tool(tool_name)
        if not tool:
            raise MCPPermissionDenied(f"Tool '{tool_name}' not found or not permitted")

        # Execute tool with context
        result = tool.execute(context, arguments)

        return {
            "content": [
                {
                    "type": "text",
                    "text": result,
                }
            ],
            "isError": False,
        }
