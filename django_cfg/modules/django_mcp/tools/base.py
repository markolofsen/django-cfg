"""Base MCP Tool Class."""

from abc import ABC, abstractmethod
from typing import Any, Dict

from django_cfg.modules.django_mcp.services.context import MCPContext
from django_cfg.modules.django_mcp.services.redactor import redactor, RedactionMode


class MCPTool(ABC):
    """Base class for all MCP tools."""

    name: str = ""
    description: str = ""
    input_schema: Dict[str, Any] = {}

    def to_definition(self) -> Dict[str, Any]:
        """Return tool definition for MCP tools/list response."""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema,
        }

    @abstractmethod
    def execute(self, context: MCPContext, arguments: Dict[str, Any]) -> str:
        """Execute the tool and return result as string."""
        pass

    def execute_with_redaction(self, context: MCPContext, arguments: Dict[str, Any]) -> str:
        """Execute tool and apply redaction to result."""
        result = self.execute(context, arguments)
        # Apply redaction based on context config
        mode = RedactionMode(context.config.redaction.mode.lower())
        return redactor.redact_string(result, mode)


class MCPToolRegistry:
    """Registry for MCP tools."""

    def __init__(self):
        self._tools: Dict[str, MCPTool] = {}

    def register(self, tool: MCPTool):
        """Register a tool."""
        self._tools[tool.name] = tool

    def unregister(self, tool_name: str):
        """Unregister a tool."""
        self._tools.pop(tool_name, None)

    def get_tool(self, name: str) -> MCPTool:
        """Get tool by name."""
        return self._tools.get(name)

    def get_all_tools(self, context: MCPContext) -> list:
        """Get all tools available for the current context."""
        # In future: filter based on user permissions
        return list(self._tools.values())


# Global tool registry instance
tool_registry = MCPToolRegistry()
