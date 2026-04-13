"""
MCP Configuration for Django-CFG Project
==========================================

All agent access is configured HERE in ONE place.
Agents can only access what's explicitly allowed below.

📍 This file is auto-discovered when placed in project root as:
   project_root/mcp/__init__.py

Quick Start:
    1. Expose models: mcp.expose("app.Model")
    2. Allow commands: mcp.allow_command("clearsessions")
    3. Define tools: @mcp.tool(...)
    4. Enable introspection: mcp.enable_introspection()
"""

from django_cfg.modules.django_mcp import MCPConfigBuilder

# Create global builder instance
mcp = MCPConfigBuilder()

# ============================================================================
# CONFIGURE AGENT ACCESS BELOW
# ============================================================================

# 1. Expose models that agents can query
# mcp.expose("profiles.UserProfile", read_only=True, max_results=50)
# mcp.expose("accounts.User", read_only=True, hidden_fields=["password", "secret_key"])
# mcp.expose("orders.Order", operations=["list", "retrieve", "create"])

# 2. Allow management commands
# mcp.allow_command("clearsessions")
# mcp.allow_command("update_stats", staff_only=True)

# 3. Enable introspection (agents can discover app structure)
# mcp.enable_introspection(expose_urls=True, expose_code=False)

# 4. Require JWT authentication (default: True)
# mcp.require_authentication()

# 5. Define custom tools
# @mcp.tool(
#     name="get_system_info",
#     description="Get system information",
# )
# def get_system_info(ctx) -> str:
#     return "System info here"

# Build final config (DO NOT REMOVE)
mcp_config = mcp.build()
