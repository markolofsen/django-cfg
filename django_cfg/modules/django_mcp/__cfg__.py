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


class MCPTargetConfig(BaseModel):
    """One endpoint an assistant can be registered against.

    Declared by the *project*, because only the project knows that production is
    ``api.example.com`` and that its key lives in ``deploy/.env``. django_cfg
    owns the machinery in ``install/``; hardcoding hostnames there would make
    the framework know about one product.

    Targets are separate **registrations**, not one setting with a flag. They
    carry distinct ``server_name``s so both can be installed at once: sharing a
    name, they silently replace each other, and an assistant then reports
    ConnectionRefused for a server nobody touched.
    """
    model_config = ConfigDict(extra="forbid", frozen=True)

    url: Optional[str] = Field(
        default=None,
        description=(
            "This deployment's base URL or full MCP endpoint. Pass the value "
            "from your own environment config, exactly as you pass `api_url` "
            "to DjangoConfig. Omit it for the local target — the running "
            "process is that deployment, so its own api_url answers."
        ),
    )
    access_key: Optional[str] = Field(
        default=None,
        repr=False,
        description=(
            "This deployment's MCP access key. Pass it from your environment "
            "config alongside `url`.\n\n"
            "It must be given explicitly for a REMOTE target, and the reason is "
            "the bug this whole field exists to prevent: `manage.py "
            "mcp_install --prod` runs on a laptop, where the loaded environment "
            "is the *development* one. Falling back to the running process's "
            "key there registers the dev key against production — the client "
            "connects, lists every tool, and 401s on the first real call, "
            "inside an assistant where nobody sees the status code.\n\n"
            "Omit it for the local target, where the process IS the deployment."
        ),
    )
    env_files: List[str] = Field(
        default_factory=list,
        description=(
            "Fallback: dotenv files to read `url`/`access_key` from when they "
            "are not passed directly, highest priority first; relative paths "
            "resolve against BASE_DIR. Useful when a deployment's secrets live "
            "outside the Django project (a compose `.env`, say) and so are "
            "never loaded into this process at all."
        ),
    )
    server_name: Optional[str] = Field(
        default=None,
        description=(
            "Registration name override. Normally omitted — it is derived as "
            "<project>_<target>. Set it to keep an existing registration: "
            "changing this name orphans the old entry rather than updating it."
        ),
    )

    @field_validator("url")
    @classmethod
    def _must_be_http(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        if not value.startswith(("http://", "https://")):
            raise ValueError(f"target url must be http(s), got {value!r}")
        # 'localhost' resolves to IPv6 ::1 first on macOS while runserver binds
        # IPv4 only, so the assistant reports ConnectionRefused against a server
        # curl reaches without trouble. Caught here rather than in support.
        if "//localhost" in value:
            raise ValueError(
                "use 127.0.0.1 rather than 'localhost': on macOS the name "
                "resolves to IPv6 ::1 first, but runserver binds IPv4 only, so "
                "assistants report ConnectionRefused against a working server"
            )
        return value


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
    service_username: Optional[str] = Field(
        default=None,
        description=(
            "Username the access key acts as. When None (the default) a valid "
            "key authenticates to AnonymousUser, so tools gated on "
            "`user.is_staff` refuse. Set this to bind the key to a real, "
            "auditable service account instead of widening those gates."
        ),
    )
    rate_limit: str = Field(
        default="100/minute",
        description="Rate limit for MCP requests",
    )
    # REMOVED: allow_unauthenticated - use access_key instead

    install_targets: Dict[str, MCPTargetConfig] = Field(
        default_factory=dict,
        description=(
            "Endpoints `manage.py mcp_install --<name>` can register, keyed by "
            "the flag that selects them (e.g. 'local', 'prod'). Empty means the "
            "command only accepts an explicit --url."
        ),
    )

    @field_validator("install_targets")
    @classmethod
    def _server_names_must_be_unique(
        cls, targets: Dict[str, "MCPTargetConfig"]
    ) -> Dict[str, "MCPTargetConfig"]:
        """Two targets sharing a server_name is a silent uninstall.

        Both write the same key in the assistant's config, so installing the
        second removes the first without a word — and the failure surfaces later
        as a connection error against an endpoint nobody changed.
        """
        seen: Dict[str, str] = {}
        for kind, target in targets.items():
            if target.server_name is None:
                # Derived names are <project>_<kind> and unique by construction.
                continue
            if (previous := seen.get(target.server_name)) is not None:
                raise ValueError(
                    f"targets {previous!r} and {kind!r} share server_name "
                    f"{target.server_name!r}; installing one would silently "
                    "deregister the other"
                )
            seen[target.server_name] = kind
        return targets

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
