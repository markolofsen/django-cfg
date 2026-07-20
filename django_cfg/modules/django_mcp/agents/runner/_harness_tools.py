"""Wrap django_mcp ``MCPTool``s as pydantic-ai tools for the harness.

The old hand-rolled runner built OpenAI ``{"type":"function",...}`` dicts and
duck-typed the provider's tool-call wire format itself. The harness owns that loop
now, so instead we hand it real ``pydantic_ai.Tool`` objects. Each wraps one
``MCPTool``: the JSON ``input_schema`` becomes the tool's parameter schema via
``Tool.from_schema``, and the callable runs ``tool.execute(context, arguments)`` with
the full MCP context pulled off the run's deps.

``MCPTool.execute`` is synchronous and may touch the ORM, so it runs in a thread
(``sync_to_async``) — a pydantic-ai tool coroutine that blocked on the DB would stall
the event loop the streaming path drives.
"""

from __future__ import annotations

import logging
from typing import Any

from asgiref.sync import sync_to_async
from pydantic_ai import RunContext, Tool

logger = logging.getLogger(__name__)


def build_harness_tools(tools: dict[str, Any]) -> list[Tool]:
    """Turn a ``{name: MCPTool}`` map into pydantic-ai ``Tool`` objects.

    The harness calls these like any other tool; the deps injected into the run
    carry the MCP context each ``MCPTool.execute`` needs.
    """
    return [_wrap_one(name, tool) for name, tool in tools.items()]


def _wrap_one(name: str, mcp_tool: Any) -> Tool:
    async def _run(ctx: RunContext[Any], **kwargs: Any) -> str:
        # The MCP context lives on the deps; execute is sync + ORM-touching, so hop
        # to a thread. Errors become a tool-result string (never raise into the loop)
        # — the same contract the old runner's _execute_tool had, so the model can
        # read the failure and recover instead of the whole run dying.
        mcp_context = getattr(ctx.deps, "context", None)
        try:
            return await sync_to_async(mcp_tool.execute, thread_sensitive=True)(
                mcp_context, kwargs,
            )
        except Exception as exc:  # noqa: BLE001 - surfaced to the model, not swallowed
            logger.exception("[django_mcp] tool %s failed", name)
            return f"Error executing {name}: {exc}"

    schema = getattr(mcp_tool, "input_schema", None) or {
        "type": "object", "properties": {}
    }
    return Tool.from_schema(
        function=_run,
        name=name,
        description=getattr(mcp_tool, "description", "") or "",
        json_schema=schema,
        takes_ctx=True,
    )
