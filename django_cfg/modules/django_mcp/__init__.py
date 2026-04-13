"""Django MCP Module - Model Context Protocol integration."""

default_app_config = "django_cfg.modules.django_mcp.apps.DjangoMCPConfig"

from .exceptions import MCPError, MCPPermissionDenied, MCPValidationError
from .__cfg__ import (
    DjangoMCPModuleConfig,
    AppMCPConfig,
    ModelMCPConfig,
    IntrospectionConfig,
    CommandMCPConfig,
    RedactionConfig,
)
from .auto_loader import load_project_mcp_config, mcp_config_exists
from .config_builder import MCPConfigBuilder


def is_enabled() -> bool:
    """Check if MCP module is enabled."""
    from django_cfg.core.state import get_current_config
    config = get_current_config()
    return config.mcp is not None and config.mcp.enabled


def get_mcp_config():
    """Get MCP configuration."""
    from django_cfg.core.state import get_current_config
    config = get_current_config()
    if config.mcp is None:
        raise MCPError("MCP module is not enabled")
    return config.mcp


def discover_and_load_project_mcp():
    """
    Automatically discover and load mcp/ folder from project root.
    
    Searches for mcp/__init__.py in the project directory and imports
    its mcp_config variable if found.
    """
    return load_project_mcp_config()


__all__ = [
    "MCPError",
    "MCPPermissionDenied",
    "MCPValidationError",
    "DjangoMCPModuleConfig",
    "AppMCPConfig",
    "ModelMCPConfig",
    "IntrospectionConfig",
    "CommandMCPConfig",
    "RedactionConfig",
    "MCPConfigBuilder",
    "is_enabled",
    "get_mcp_config",
    "discover_and_load_project_mcp",
]
