"""One wrapper around every tool call: a wall-clock limit, and a failure the model can read.

pydantic-ai runs a tool and lets its exception end the whole answer; a sync tool that hangs holds the answer until the run's own
timeout. `tool_guard_capability` wraps `wrap_tool_execute`:

* **Timeout.** The limit of the tool (`ToolMeta.resolved_timeout()` when the tool carries a `ToolMeta`, else the default) is
  enforced. An async tool is cancelled. A sync tool runs in a worker thread that cannot be killed: it is abandoned and its
  result is discarded, so it should not hold a lock or a transaction past the call. Either way the model reads
  `tool_timeout: ...` as a failed tool result and can answer without it.
* **Exceptions.** Any other exception of the tool body becomes `tool_error: <ExceptionType>` for the model (the type only, never the message,
  which can hold SQL or a path) and a traceback in the log. `ModelRetry`, `ToolFailed` and the deferral exceptions pass through: they are
  the tool's own way of talking to the loop.

The failure goes out as `ToolFailed`: the model sees a failed result and does not spend the tool's retry budget on it.
Cancellation of the whole run is never swallowed.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Mapping
from typing import Any

from pydantic_ai.capabilities import Hooks
from pydantic_ai.exceptions import (
    ApprovalRequired,
    CallDeferred,
    ModelRetry,
    SkipToolExecution,
    ToolFailed,
    ToolRetryError,
)

logger = logging.getLogger(__name__)

TOOL_TIMEOUT = "tool_timeout"
TOOL_ERROR = "tool_error"

#: The tool's own control flow: not a failure.
_PASS_THROUGH = (ModelRetry, ToolFailed, ToolRetryError, CallDeferred, ApprovalRequired, SkipToolExecution)


def tool_guard_capability(*, timeouts: Mapping[str, float] | None = None, default_timeout_s: float | None = 30.0) -> Hooks[Any]:
    """The guard for one run. `timeouts` is the per-tool limit in seconds by tool name; `default_timeout_s` covers the rest
    (None or 0: no limit for a tool with none of its own)."""
    per_tool = dict(timeouts or {})

    async def guard(ctx: Any, *, call: Any, tool_def: Any, args: Any, handler: Any) -> Any:
        name = call.tool_name
        limit = per_tool.get(name, default_timeout_s)
        try:
            if not limit:
                return await handler(args)
            task = asyncio.ensure_future(handler(args))
            try:
                done, _ = await asyncio.wait({task}, timeout=float(limit))
            except BaseException:  # the run was cancelled while waiting: the tool goes with it
                task.cancel()
                raise
            if not done:
                task.cancel()
                logger.warning("[tool_guard] %s stopped after %.1fs", name, float(limit))
                raise ToolFailed(f"{TOOL_TIMEOUT}: {name} took longer than {limit:g} s and was stopped. Try a smaller request, or answer without it.")
            return task.result()
        except _PASS_THROUGH:
            raise
        except Exception as exc:  # noqa: BLE001 - one tool must not end the answer
            logger.exception("[tool_guard] %s raised %s", name, type(exc).__name__)
            raise ToolFailed(f"{TOOL_ERROR}: {name} failed ({type(exc).__name__}). Answer without it, or try different arguments.") from exc

    return Hooks(tool_execute=guard)
