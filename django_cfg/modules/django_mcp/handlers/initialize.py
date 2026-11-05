"""MCP Initialize Handler."""

from typing import Any, Dict, Optional

from django_cfg.modules.django_mcp.protocols.types import (
    MCPServerInfo,
    MCPCapabilities,
    MCPInitializeResult,
)
from django_cfg.modules.django_mcp.registries import prompt_registry, resource_registry
from django_cfg.modules.django_mcp.services.context import MCPContext


def resolve_server_name(explicit: Any = None) -> str:
    """The connector name clients show: ``server_name`` if set, else the project slug."""
    if explicit:
        return explicit
    from django_cfg.core.state import get_current_config

    config = get_current_config()
    return getattr(config, "project_slug", None) or "mcp"


def _field(config: Any, name: str) -> Any:
    return config.get(name) if isinstance(config, dict) else getattr(config, name, None)


def resolve_instructions(config: Any, profile: Any = None) -> Optional[str]:
    """Profile text, else config text, then every remote manifest's, joined by a blank line."""
    from django_cfg.modules.django_mcp.remote import remote_instructions

    own = getattr(profile, "instructions", None) or _field(config, "instructions")
    parts = [own] if own else []
    parts += remote_instructions(profile)
    return "\n\n".join(parts) or None


class InitializeHandler:
    """Handle MCP initialize handshake."""

    @staticmethod
    def handle_initialize(params: Dict[str, Any], context: MCPContext) -> Dict[str, Any]:
        """
        Handle the MCP initialization handshake.

        This is the first call every MCP client must make to negotiate
        protocol version and discover server capabilities.
        """
        config = context.config
        # Handle both dict and model instances
        if isinstance(config, dict):
            introspection = config.get("introspection", {})
            server_name = resolve_server_name(config.get("server_name"))
            server_version = config.get("server_version", "1.0.0")
            protocol_version = config.get("protocol_version", "2025-03-26")
            if isinstance(introspection, dict):
                introspection_enabled = introspection.get("enabled", False)
            else:
                introspection_enabled = getattr(introspection, "enabled", False)
        else:
            introspection = config.introspection
            server_name = resolve_server_name(config.server_name)
            server_version = config.server_version
            protocol_version = config.protocol_version
            if isinstance(introspection, dict):
                introspection_enabled = introspection.get("enabled", False)
            else:
                introspection_enabled = introspection.enabled

        # Build capabilities based on configuration
        profile = getattr(context, "profile", None)
        capabilities = MCPCapabilities(tools={"listChanged": False})

        exposed = _field(config, "exposed_apps")
        if resource_registry.visible(profile) or (introspection_enabled and exposed):
            capabilities.resources = {"listChanged": False}

        if prompt_registry.visible(profile):
            capabilities.prompts = {"listChanged": False}

        # Build server info
        server_info = MCPServerInfo(
            name=server_name,
            version=server_version,
        )

        # Build result
        result = MCPInitializeResult(
            protocolVersion=protocol_version,
            capabilities=capabilities,
            serverInfo=server_info,
            instructions=resolve_instructions(config, profile),
        )

        # exclude_none is required, not cosmetic. Every capability is Optional,
        # so a plain model_dump() emits `"logging": null` for the ones this
        # server does not implement. The MCP schema types a capability as an
        # object, and a strict client rejects the whole handshake: Claude Code
        # fails with `capabilities.logging: Invalid input` and never connects.
        # An absent key means "not supported"; null is simply invalid.
        return result.model_dump(exclude_none=True)
