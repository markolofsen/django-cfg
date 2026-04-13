"""MCP Module Configuration."""

from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class ModelMCPConfig(BaseModel):
    """Configuration for exposing a single Django model to MCP."""
    model_config = ConfigDict(extra="forbid", frozen=True)

    enabled: bool = Field(
        default=False,
        description="Whether this model is exposed to MCP",
    )
    read_only: bool = Field(
        default=True,
        description="If True, only read operations are allowed",
    )
    hidden_fields: List[str] = Field(
        default_factory=list,
        description="Fields to exclude from MCP responses (e.g., password, secret_key)",
    )
    max_results: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Maximum number of records returned per query",
    )
    allowed_operations: List[str] = Field(
        default_factory=lambda: ["list", "retrieve"],
        description="Allowed CRUD operations: list, retrieve, create, update, delete",
    )


class AppMCPConfig(BaseModel):
    """Configuration for exposing a Django app to MCP."""
    model_config = ConfigDict(extra="forbid", frozen=True)

    enabled: bool = Field(
        default=False,
        description="Whether this app's models are exposed to MCP",
    )
    models: Dict[str, ModelMCPConfig] = Field(
        default_factory=dict,
        description="Per-model configuration. Key is model name (lowercase)",
    )
    max_results: int = Field(
        default=100,
        description="Default max_results for all models in this app",
    )


class IntrospectionConfig(BaseModel):
    """Configuration for Django introspection capabilities."""
    model_config = ConfigDict(extra="forbid", frozen=True)

    enabled: bool = Field(
        default=False,
        description="Allow agents to discover app structure",
    )
    expose_urls: bool = Field(
        default=False,
        description="Expose URL patterns to agents",
    )
    expose_code: bool = Field(
        default=False,
        description="Expose view source code snippets (dev only!)",
    )
    max_depth: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum depth of relationship traversal",
    )


class CommandMCPConfig(BaseModel):
    """Configuration for management command execution."""
    model_config = ConfigDict(extra="forbid", frozen=True)

    enabled: bool = Field(
        default=False,
        description="Allow agents to execute management commands",
    )
    allowed_commands: List[str] = Field(
        default_factory=list,
        description="Whitelist of allowed command names",
    )
    timeout_seconds: int = Field(
        default=30,
        ge=1,
        le=300,
        description="Maximum execution time per command",
    )


class RedactionConfig(BaseModel):
    """Configuration for automatic PII redaction."""
    model_config = ConfigDict(extra="forbid", frozen=True)

    enabled: bool = Field(
        default=True,
        description="Enable automatic PII redaction",
    )
    mode: str = Field(
        default="REDACT",
        pattern="^(NONE|REDACT|BLOCK)$",
        description="NONE=pass, REDACT=mask, BLOCK=reject",
    )
    custom_patterns: Dict[str, str] = Field(
        default_factory=dict,
        description="Additional regex patterns to redact. Name -> pattern",
    )


class DjangoMCPModuleConfig(BaseModel):
    """
    Global configuration for the Model Context Protocol module.

    This module transforms Django into an MCP server, enabling AI agents
    to discover and interact with application data through a standardized protocol.
    """
    model_config = ConfigDict(extra="forbid", frozen=False)

    enabled: bool = Field(
        default=False,
        description="Master switch for MCP module",
    )
    endpoint_path: str = Field(
        default="/cfg/mcp/",
        pattern=r"^/[^\s]+$",
        description="URL path for MCP endpoint",
    )
    # LLM Configuration for AI agents
    llm_model: str = Field(
        default="openai/gpt-4.1-nano",
        description="Default LLM model for MCP agents (OpenRouter format)",
    )

    access_key: Optional[str] = Field(
        default=None,
        description="Static access key for agents (passed via X-MCP-Access-Key header). Required.",
        repr=False,
    )
    rate_limit: str = Field(
        default="100/minute",
        description="Rate limit for MCP requests",
    )
    # REMOVED: allow_unauthenticated - use access_key instead

    # Introspection
    introspection: IntrospectionConfig = Field(
        default_factory=IntrospectionConfig,
        description="Django structure discovery settings",
    )

    # App-level exposure
    exposed_apps: Dict[str, AppMCPConfig] = Field(
        default_factory=dict,
        description="Per-app MCP configuration",
    )

    # Management commands
    commands: CommandMCPConfig = Field(
        default_factory=CommandMCPConfig,
        description="Management command execution settings",
    )

    # Data protection
    redaction: RedactionConfig = Field(
        default_factory=RedactionConfig,
        description="Automatic PII redaction settings",
    )

    # Advanced
    protocol_version: str = Field(
        default="2025-03-26",
        description="MCP protocol version to support",
    )
    server_name: str = Field(
        default="django-cfg-mcp",
        description="Server name reported in initialize handshake",
    )
    server_version: str = Field(
        default="1.0.0",
        description="Server version reported in initialize handshake",
    )
    enable_streaming: bool = Field(
        default=False,
        description="Enable SSE streaming for agent responses",
    )
    enable_audit_log: bool = Field(
        default=True,
        description="Log all MCP operations for security auditing",
    )

    @field_validator("rate_limit")
    @classmethod
    def validate_rate_limit(cls, v: str) -> str:
        """Validate rate limit format: 'count/period'."""
        parts = v.split("/")
        if len(parts) != 2:
            raise ValueError("Rate limit must be in format: 'count/period' (e.g., '10/minute')")
        count = int(parts[0])
        period = parts[1]
        if count < 1:
            raise ValueError("Rate limit count must be positive")
        if period not in ("second", "minute", "hour", "day"):
            raise ValueError(f"Period must be one of: second, minute, hour, day")
        return v

    def is_model_exposed(self, app_label: str, model_name: str) -> bool:
        """Check if a specific model is exposed to MCP."""
        app_config = self.exposed_apps.get(app_label)
        if not app_config or not app_config.enabled:
            return False
        model_config = app_config.models.get(model_name.lower())
        return model_config is not None and model_config.enabled

    def get_model_config(self, app_label: str, model_name: str) -> Optional[ModelMCPConfig]:
        """Get configuration for a specific model."""
        app_config = self.exposed_apps.get(app_label)
        if not app_config:
            return None
        return app_config.models.get(model_name.lower())

    def is_command_allowed(self, command_name: str) -> bool:
        """Check if a management command is whitelisted."""
        return (
            self.commands.enabled
            and command_name in self.commands.allowed_commands
        )
