"""MCP Initialize Handler."""

from typing import Any, Dict

from django_cfg.modules.django_mcp.protocols.types import (
    MCPServerInfo,
    MCPCapabilities,
    MCPInitializeResult,
)
from django_cfg.modules.django_mcp.services.context import MCPContext


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
            server_name = config.get("server_name", "django-cfg-mcp")
            server_version = config.get("server_version", "1.0.0")
            protocol_version = config.get("protocol_version", "2025-03-26")
            if isinstance(introspection, dict):
                introspection_enabled = introspection.get("enabled", False)
            else:
                introspection_enabled = getattr(introspection, "enabled", False)
        else:
            introspection = config.introspection
            server_name = config.server_name
            server_version = config.server_version
            protocol_version = config.protocol_version
            if isinstance(introspection, dict):
                introspection_enabled = introspection.get("enabled", False)
            else:
                introspection_enabled = introspection.enabled

        # Build capabilities based on configuration
        capabilities = MCPCapabilities(
            tools={"listChanged": False},
            resources={"listChanged": False},
        )

        if introspection_enabled:
            capabilities.prompts = {}

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
        )

        # exclude_none is required, not cosmetic. Every capability is Optional,
        # so a plain model_dump() emits `"logging": null` for the ones this
        # server does not implement. The MCP schema types a capability as an
        # object, and a strict client rejects the whole handshake: Claude Code
        # fails with `capabilities.logging: Invalid input` and never connects.
        # An absent key means "not supported"; null is simply invalid.
        return result.model_dump(exclude_none=True)
