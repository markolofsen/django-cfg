"""Deps for a django_mcp harness run.

The harness reads only a few attributes off the run deps — ``action_guard_policy``,
``expose_tool_events``, ``search_ctx`` — all via ``getattr`` with safe defaults, so a
host that has no mutation-guard or RAG concept (django_mcp) needs none of CRM's full
deps machinery. The one thing django_mcp DOES need on the deps is ``context``: its
wrapped tools receive the full MCP context from it (see ``_harness_tools``).

Kept deliberately minimal — a fourth field here would be a hint the harness is asking
django_mcp for something a simpler tool host shouldn't have to provide.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class MCPAgentDeps:
    """What a django_mcp harness run carries. Passed into every wrapped tool."""

    #: Full MCP request context passed to ``MCPTool.execute(context, args)``.
    context: Any = None
