"""Base MCP Tool Class."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

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

    def is_available(self, context: Optional[MCPContext]) -> bool:
        """Whether this tool should appear in ``tools/list`` at all.

        Default: always. Override when a tool can be configured *off*, so it
        disappears from the listing instead of being advertised and failing on
        every call.

        That distinction matters more than it looks. An agent reads a listed
        tool as a capability; when calling it always errors, the agent does not
        conclude "this feature is disabled here" — it concludes the server is
        broken, and may stop trusting neighbouring tools that do work. A tool
        that is not listed is simply a capability this deployment lacks.
        """
        return True

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

    def get_all_tools(self, context: Optional[MCPContext]) -> list:
        """Tools this context may see.

        Registration happens at import time, when there is no config to consult,
        so a tool that can be switched off is registered anyway and filtered
        here — the first point where the context exists.

        Note this filters on *configuration*, not on the caller: the registry
        still has no per-key tenancy, so every authenticated caller sees the
        same set.

        ``context`` may be ``None``: the public ``/info/`` view lists tools
        before there is a caller. Every ``is_available`` implementation must
        therefore tolerate it — one that dereferenced ``context.config``
        directly turned ``/info/`` into a 500 on every upgraded deployment,
        and because that view answers *before* authentication it broke for
        everyone while the authenticated surface stayed green.
        """
        return [tool for tool in self._tools.values() if tool.is_available(context)]


# Global tool registry instance
tool_registry = MCPToolRegistry()
