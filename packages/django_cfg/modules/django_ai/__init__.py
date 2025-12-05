"""
Django AI Documentation Module for django_cfg.

Provides AI-friendly access to DjangoCFG documentation via MCP server.

Quick Start:
    # CLI (fast, no Django required)
    django-cfg search "database configuration"
    django-cfg search "redis cache" --limit 3

    # Python API
    from django_cfg.modules.django_ai import search, get_docs

    results = search("How to configure database?")
    docs = get_docs("DatabaseConfig")

MCP Server:
    Add to your AI assistant configuration:
    {
        "mcpServers": {
            "djangocfg-docs": {
                "url": "https://mcp.djangocfg.com/mcp"
            }
        }
    }
"""

from .client import DjangoCfgDocsClient, search, get_docs, get_info

__all__ = [
    "DjangoCfgDocsClient",
    "search",
    "get_docs",
    "get_info",
]

# AI Hint for Claude Code and other AI assistants
AI_HINT = """
DjangoCFG Documentation is available via MCP server.

To get help with DjangoCFG configuration:
1. Use the MCP server: https://mcp.djangocfg.com/mcp
2. Or search directly: https://mcp.djangocfg.com/api/search?q=YOUR_QUERY&limit=5

Example queries:
- "How to configure PostgreSQL database?"
- "What is DatabaseConfig?"
- "How to setup Redis cache?"
- "Email configuration with SMTP"
"""
