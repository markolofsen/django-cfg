"""Base MCP Tool Class."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union

from django_cfg.modules.django_mcp.services.context import MCPContext
from django_cfg.modules.django_mcp.services.redactor import redactor, RedactionMode
from django_cfg.modules.django_mcp.tools.results import ToolResult


class MCPTool(ABC):
    """Base class for all MCP tools."""

    name: str = ""
    description: str = ""
    input_schema: Dict[str, Any] = {}

    #: Whether the public profile may serve this tool.
    #:
    #: **Defaults to False, and the default is the design.** A tool declared
    #: beside its own code is the only place that knows whether it is safe to
    #: expose; a list kept in the project's config is a second place, and the
    #: two drift the moment someone adds a tool without editing it. Silently,
    #: and in the direction that publishes an operator capability.
    #:
    #: Set True only for a tool that reads data already public, returns no
    #: personal data, and cannot mutate anything.
    public: bool = False

    #: What the tool does to the world, declared next to its code like `public`.
    #:
    #: Clients (Claude, ChatGPT, Codex) read these four hints to decide whether a
    #: call needs the user's confirmation: a read-only tool runs without asking,
    #: a tool that may change data always asks. A tool that declares nothing is
    #: treated as a writer, so the safe default also nags: mark every reader.
    #: `read_only`: only reads, no side effect on its environment.
    #: `destructive`: may delete or overwrite (None = yes unless `read_only`).
    #: `idempotent`: a repeated call with the same arguments changes nothing more.
    #: `open_world`: reaches systems outside this server (web, third-party APIs).
    #: `title`: human label for the client's tool list ("" = derived from `name`).
    read_only: bool = False
    destructive: Optional[bool] = None
    idempotent: Optional[bool] = None
    open_world: bool = False
    title: str = ""

    def annotations(self) -> Dict[str, Any]:
        """The four MCP hints, always all present (ChatGPT's review rejects a tool that omits one)."""
        destructive = (not self.read_only) if self.destructive is None else bool(self.destructive)
        idempotent = self.read_only if self.idempotent is None else bool(self.idempotent)
        return {
            "title": self.title or self.name.replace("_", " ").capitalize(),
            "readOnlyHint": bool(self.read_only),
            "destructiveHint": False if self.read_only else destructive,
            "idempotentHint": idempotent,
            "openWorldHint": bool(self.open_world),
        }

    def schema_for(self, profile) -> Dict[str, Any]:
        """The input schema this profile should be shown.

        Default: the class attribute, unchanged. Override when a limit differs
        by profile — a public surface that caps rows lower than the operator
        one must *say so*, or the listing advertises a ceiling the call will not
        honour and the agent reads the clamp as a bug.

        Tools are registered as singleton instances, so this must return a new
        dict rather than mutate ``self.input_schema``: two profiles share the
        object, and a per-request mutation is a cross-request race.
        """
        return self.input_schema

    def to_definition(self, profile=None) -> Dict[str, Any]:
        """Return tool definition for MCP tools/list response.

        ``profile`` is optional so every existing caller keeps working; when
        given, the schema is the one that profile should see.
        """
        annotations = self.annotations()
        return {
            "name": self.name,
            "title": annotations["title"],
            "description": self.description,
            "inputSchema": self.schema_for(profile) if profile is not None else self.input_schema,
            "annotations": annotations,
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
    def execute(self, context: MCPContext, arguments: Dict[str, Any]) -> Union[str, ToolResult]:
        """Execute the tool: a string (one text block) or a ``ToolResult`` (text plus image/link blocks)."""
        pass

    def execute_with_redaction(self, context: MCPContext, arguments: Dict[str, Any]) -> Union[str, ToolResult]:
        """Execute tool and apply redaction to result."""
        result = self.execute(context, arguments)
        mode = RedactionMode(context.config.redaction.mode.lower())
        if isinstance(result, ToolResult):
            result.text = redactor.redact_string(result.text, mode)
            return result
        return redactor.redact_string(result, mode)


class MCPToolRegistry:
    """Registry for MCP tools."""

    def __init__(self):
        self._tools: Dict[str, MCPTool] = {}
        # Callables returning tools that are not known at import time (a remote
        # manifest). Static tools win on a name clash.
        self._providers: list = []

    def add_provider(self, provider) -> None:
        """Add a ``() -> list[MCPTool]`` source consulted on every lookup."""
        if provider not in self._providers:
            self._providers.append(provider)

    def remove_provider(self, provider) -> None:
        if provider in self._providers:
            self._providers.remove(provider)

    def _provided(self) -> Dict[str, MCPTool]:
        out: Dict[str, MCPTool] = {}
        for provider in self._providers:
            for tool in provider():
                out.setdefault(tool.name, tool)
        return out

    def register(self, tool: MCPTool):
        """Register a tool."""
        self._tools[tool.name] = tool

    def unregister(self, tool_name: str):
        """Unregister a tool."""
        self._tools.pop(tool_name, None)

    def get_tool(self, name: str) -> MCPTool:
        """Get tool by name."""
        tool = self._tools.get(name)
        if tool is None and self._providers:
            tool = self._provided().get(name)
        return tool

    def get_all_tools(self, context: Optional[MCPContext], *, profile=None) -> list:
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

        ``profile`` narrows the result to what that surface serves. It is a
        keyword because ``/info/`` has a profile but no context, so the two
        cannot be folded into one argument.
        """
        profile = profile if profile is not None else getattr(context, "profile", None)
        every = dict(self._tools)
        if self._providers:
            for name, tool in self._provided().items():
                every.setdefault(name, tool)
        tools = [tool for tool in every.values() if tool.is_available(context)]
        if profile is not None and not profile.serves_all_tools:
            # The tool object, not its name: `PUBLIC_TOOLS` resolves by reading
            # the tool's own `public` flag.
            tools = [tool for tool in tools if profile.serves(tool)]
        return tools


# Global tool registry instance
tool_registry = MCPToolRegistry()
