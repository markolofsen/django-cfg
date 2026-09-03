"""MCP Tools Handler."""

import logging
import time
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

logger = logging.getLogger(__name__)


def _caller_ip(context) -> str:
    """Best-effort caller address for the access log.

    An anonymous profile has no key and no account, so the address is the only
    thing distinguishing one caller from another when reading the log after the
    fact. ``X-Forwarded-For`` is trusted here only because this endpoint sits
    behind the deployment's own proxy; it is a log field, never an auth input.
    """
    request = getattr(context, "request", None)
    if request is None:
        return "-"
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR") or "-"

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
            tools.append(tool.to_definition(getattr(context, "profile", None)))

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

        # Filtering the LISTING is cosmetic on its own: a caller who learned an
        # operator tool's name from documentation, another deployment or a leaked
        # `/info/` could still invoke it here. The profile decides what exists,
        # not merely what is advertised.
        #
        # Reported as "not found" rather than "forbidden" because from this
        # profile's perspective it genuinely does not exist — and a permission
        # error would confirm the tool is real, which is what the filtered
        # listing set out to withhold.
        profile = getattr(context, "profile", None)
        if profile is not None and not profile.serves(tool):
            logger.info(
                "mcp.call profile=%s tool=%s ip=%s outcome=refused",
                getattr(profile, "name", "-"),
                tool_name,
                _caller_ip(context),
            )
            raise MCPPermissionDenied(f"Tool '{tool_name}' not found or not permitted")

        # Execute tool with context
        started = time.monotonic()
        try:
            result = tool.execute(context, arguments)
        except Exception as exc:
            logger.warning(
                "mcp.call profile=%s tool=%s ip=%s args=%s ms=%d outcome=error error=%s",
                getattr(profile, "name", "-"),
                tool_name,
                _caller_ip(context),
                ",".join(sorted(arguments)) or "-",
                (time.monotonic() - started) * 1000,
                type(exc).__name__,
            )
            raise

        logger.info(
            "mcp.call profile=%s tool=%s ip=%s args=%s ms=%d bytes=%d outcome=ok",
            getattr(profile, "name", "-"),
            tool_name,
            _caller_ip(context),
            # Argument NAMES only. On an anonymous endpoint the values are
            # attacker-supplied and may carry a search phrase or an id a caller
            # would not expect us to retain; the names are enough to tell which
            # shape of call was made.
            ",".join(sorted(arguments)) or "-",
            (time.monotonic() - started) * 1000,
            len(result or ""),
        )

        return {
            "content": [
                {
                    "type": "text",
                    "text": result,
                }
            ],
            "isError": False,
        }
