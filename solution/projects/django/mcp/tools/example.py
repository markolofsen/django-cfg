"""
Example MCP Tools for Carapis Project

These tools are auto-discovered and registered at Django startup.
"""

import json
from typing import Any, Dict

from django_cfg.modules.django_mcp.tools.base import MCPTool, tool_registry


class GetProjectStatsTool(MCPTool):
    """
    Get project statistics summary.
    Example project-specific tool.
    """

    name = "get_project_stats"
    description = "Get project statistics: total users, active sessions, etc."
    input_schema = {
        "type": "object",
        "properties": {},
    }

    def execute(self, context: Any, arguments: Dict[str, Any]) -> str:
        """Execute the get_project_stats tool."""
        from django.contrib.auth import get_user_model

        User = get_user_model()
        stats = {
            "total_users": User.objects.count(),
            "active_users": User.objects.filter(is_active=True).count(),
        }

        return json.dumps(stats, indent=2)


# Auto-register when this module is imported
tool_registry.register(GetProjectStatsTool())
