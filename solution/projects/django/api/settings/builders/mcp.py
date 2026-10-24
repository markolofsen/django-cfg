"""MCP configuration — what agents may reach, and under which key.

Split out of ``api/settings/config.py`` into its own module for the same
reason ``admin.py``/``background.py``/``openapi.py`` were: it is a self
contained declaration that does not need reading to understand how the
project boots.

MCP config is intentionally declared here rather than auto-discovered from a
project ``mcp/`` package — one declaration, nothing to disagree with.
"""

from __future__ import annotations

from django_cfg import (
    DjangoMCPModuleConfig,
    MCPCommandMCPConfig,
    MCPIntrospectionConfig,
    MCPRedactionConfig,
)


def build_mcp_config():
    """Build the project's MCP config. Called once, from ``config.py``."""
    if not DjangoMCPModuleConfig:
        return None

    return DjangoMCPModuleConfig(
        enabled=True,
        access_key="dev-key-test",  # Development key only
        introspection=MCPIntrospectionConfig(enabled=True, expose_urls=True),
        exposed_apps={},
        commands=MCPCommandMCPConfig(
            enabled=False,
            allowed_commands=[],
            timeout_seconds=30,
        ),
        redaction=MCPRedactionConfig(
            enabled=True,
            mode="REDACT",
            custom_patterns={},
        ),
    )
