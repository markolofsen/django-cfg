"""MCP package — tools only.

**The configuration is not here.** Models exposed, the access key, the
introspection switch and the LLM model are declared once, in
``api/settings/mcp_config.py``, and reach Django through the ``mcp:`` field of
``api/settings/config.py``.

It moved out of this file on 2026-09-02. While both existed, two objects
declared the same config and the wrong one could win silently:
``MCPConfig.ready()`` replaces the settings field with whatever this
module builds — but only if this module imports cleanly, and
``auto_loader.load_project_mcp_config()`` catches *every* exception and returns
``None``. An ImportError here therefore left the other declaration live while
every log line reported MCP as configured. The sibling service hit exactly
that, serving real data under a committed key.

Tools in ``mcp/tools/`` are still auto-discovered — that half was never
ambiguous. Adding a tool means adding a module there; it needs no registration
in this file.

Delivery track: ``@dev/planned/mcp-operator-surface/PLAN.md``.
"""
