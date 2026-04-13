"""
MCP Configuration Builder

Simple declarative API for configuring agent access in ONE place.
"""

from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from functools import wraps

from django_cfg.modules.django_mcp import (
    DjangoMCPModuleConfig,
    IntrospectionConfig,
    AppMCPConfig,
    ModelMCPConfig,
    CommandMCPConfig,
)
from django_cfg.modules.django_mcp.tools.base import MCPTool, tool_registry
from django_cfg.modules.django_mcp.services.context import MCPContext


@dataclass
class ModelExposure:
    """Configuration for exposing a single model."""
    app_label: str
    model_name: str
    read_only: bool = True
    hidden_fields: List[str] = field(default_factory=list)
    max_results: int = 100
    operations: List[str] = field(default_factory=lambda: ["list", "retrieve"])
    description: str = ""


class MCPConfigBuilder:
    """
    Simple builder for MCP configuration.

    All agent access is configured here in ONE place.
    Place this in project_root/mcp/__init__.py

    Example:
        from django_cfg.modules.django_mcp import MCPConfigBuilder

        mcp = MCPConfigBuilder()

        # Expose models
        mcp.expose("profiles.UserProfile")
        mcp.expose("accounts.User", hidden_fields=["password", "secret_key"])
        mcp.expose("orders.Order", operations=["list", "retrieve", "create"])

        # Allow commands
        mcp.allow_command("clearsessions")
        mcp.allow_command("update_stats", staff_only=True)

        # Custom tools
        @mcp.tool(name="get_user_stats", description="Get user statistics")
        def get_user_stats(ctx, user_id: str) -> str:
            return f"Stats for user {user_id}"

        # Enable introspection
        mcp.enable_introspection(expose_urls=True)

        # Build final config
        mcp_config = mcp.build()
    """

    def __init__(self):
        self._models: Dict[str, ModelExposure] = {}
        self._commands: List[str] = []
        self._staff_commands: List[str] = []
        self._introspection: IntrospectionConfig = IntrospectionConfig()
        self._custom_tools: List[MCPTool] = []
        self._enabled: bool = True
        self._access_key: Optional[str] = None
        self._rate_limit: str = "100/minute"
        self._llm_model: str = "openai/gpt-4.1-nano"

    def expose(
        self,
        model_path: str,
        *,
        read_only: bool = True,
        hidden_fields: Optional[List[str]] = None,
        max_results: int = 100,
        operations: Optional[List[str]] = None,
        description: str = "",
    ) -> "MCPConfigBuilder":
        """
        Expose a Django model to MCP agents.

        Args:
            model_path: "app.Model" or "app_label.ModelName" (e.g., "profiles.UserProfile")
            read_only: If True, only read operations allowed
            hidden_fields: Fields to hide from agents (e.g., passwords)
            max_results: Maximum number of records returned per query
            operations: Allowed operations: list, retrieve, create, update, delete
            description: Optional description for the model
        """
        parts = model_path.split(".")
        if len(parts) != 2:
            raise ValueError(f"Invalid model path: '{model_path}'. Use 'app.Model' format.")

        app_label, model_name = parts[0], parts[1]

        if read_only and operations is None:
            operations = ["list", "retrieve"]

        self._models[model_path.lower()] = ModelExposure(
            app_label=app_label,
            model_name=model_name.lower(),
            read_only=read_only,
            hidden_fields=hidden_fields or [],
            max_results=max_results,
            operations=operations or ["list", "retrieve"],
            description=description,
        )
        return self

    def allow_command(self, command_name: str, staff_only: bool = False) -> "MCPConfigBuilder":
        """
        Allow agents to execute a management command.

        Args:
            command_name: Django management command name
            staff_only: If True, only staff users can execute this command
        """
        if staff_only:
            self._staff_commands.append(command_name)
        else:
            self._commands.append(command_name)
        return self

    def enable_introspection(
        self,
        expose_urls: bool = False,
        expose_code: bool = False,
        max_depth: int = 3,
    ) -> "MCPConfigBuilder":
        """
        Enable Django structure discovery for agents.

        Args:
            expose_urls: Expose URL patterns to agents
            expose_code: Expose view source code (NEVER in production!)
            max_depth: Maximum depth of relationship traversal
        """
        self._introspection = IntrospectionConfig(
            enabled=True,
            expose_urls=expose_urls,
            expose_code=expose_code,
            max_depth=max_depth,
        )
        return self

    def tool(self, name: str, description: str, input_schema: Optional[Dict[str, Any]] = None):
        """
        Decorator to define a custom tool for agents.

        Usage:
            @mcp.tool(name="get_stats", description="Get system statistics")
            def get_stats(ctx: MCPContext) -> str:
                return "Stats here"
        """
        if input_schema is None:
            input_schema = {"type": "object", "properties": {}}

        def decorator(func: Callable):
            class DecoratedTool(MCPTool):
                def __init__(self):
                    self.name = name
                    self.description = description
                    self.input_schema = input_schema
                    self.func = func

                def execute(self, context: MCPContext, arguments: Dict[str, Any]) -> str:
                    return self.func(context, **arguments)

            tool = DecoratedTool()
            tool_registry.register(tool)
            self._custom_tools.append(tool)

            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper

        return decorator

    def set_access_key(self, key: str) -> "MCPConfigBuilder":
        """Set static access key for agents. REQUIRED for all requests."""
        self._access_key = key
        return self

    def set_llm_model(self, model: str) -> "MCPConfigBuilder":
        """
        Set default LLM model for agents (OpenRouter format).
        Example: 'openai/gpt-4.1-nano', 'anthropic/claude-3.5-haiku'
        """
        self._llm_model = model
        return self

    def set_rate_limit(self, limit: str = "100/minute") -> "MCPConfigBuilder":
        """Set rate limit for MCP requests."""
        self._rate_limit = limit
        return self

    def disable(self) -> "MCPConfigBuilder":
        """Disable MCP module entirely."""
        self._enabled = False
        return self

    def build(self) -> Optional[DjangoMCPModuleConfig]:
        """
        Build the final DjangoMCPModuleConfig.

        Returns None if MCP is disabled.
        """
        if not self._enabled:
            return None

        # Group models by app
        exposed_apps: Dict[str, AppMCPConfig] = {}
        for model_key, exposure in self._models.items():
            app_label = exposure.app_label
            model_name = exposure.model_name

            if app_label not in exposed_apps:
                exposed_apps[app_label] = AppMCPConfig(
                    enabled=True,
                    models={},
                )

            exposed_apps[app_label].models[model_name] = ModelMCPConfig(
                enabled=True,
                read_only=exposure.read_only,
                hidden_fields=exposure.hidden_fields,
                max_results=exposure.max_results,
                allowed_operations=exposure.operations,
            )

        # All commands (staff + non-staff)
        all_commands = list(set(self._commands + self._staff_commands))

        return DjangoMCPModuleConfig(
            enabled=self._enabled,
            access_key=self._access_key,
            rate_limit=self._rate_limit,
            llm_model=self._llm_model,
            introspection=self._introspection,
            exposed_apps=exposed_apps,
            commands=CommandMCPConfig(
                enabled=len(all_commands) > 0,
                allowed_commands=all_commands,
                timeout_seconds=30,
            ),
        )
