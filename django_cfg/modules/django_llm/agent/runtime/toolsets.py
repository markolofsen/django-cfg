"""Project a host's tools into the toolsets a pydantic-ai ``Agent`` is built from.

The host supplies the tools (via its `ToolProvider` — see ``agent/protocols.py``);
this module decides *how they are presented to the model*. That presentation is
machinery, not policy — it is the same for every host:

- **eager vs deferred.** A deferred toolset's schemas are only fetched when the
  model asks for them (``search_tools(keywords=…)``). On a wide surface this is the
  difference between paying for every tool on every turn and paying for the handful
  a turn actually touches (~6 300 tokens saved on CRM's 77-tool surface for turns
  that never open the DB browser).

- **sandbox projection.** ``CodeMode`` runs whatever toolset it wraps and renders
  the wrapped tool's *declared return type* into the catalog the model reads. So
  selecting a tool by name is not enough: left as its native callable, a read tool
  would hand model code a display string and advertise ``-> str``, and the model
  would write string-handling instead of the loop the sandbox exists to run. The
  projection swaps in the structured surface. See
  ``agent/tools/core/_base_tool.py::as_sandbox_callable``.

**Only reads should ever be sandboxed.** Everything outside ``sandboxed`` stays a
native callable so ``requires_approval=True`` can still suspend the run for HITL. A
send fired from inside a sandbox loop is a send nobody approved — the sandbox
executes model code, and model code does not stop at an approval boundary.

This module knows nothing about any host's registry. It was extracted from CRM's
``tool_resolver``, which fetched the tools AND projected them — and so could not be
shared, and duplicated the `ToolProvider` seam while it was at it.
"""

from __future__ import annotations

import logging
from typing import Any, Callable

logger = logging.getLogger(__name__)


def build_toolsets(
    base: list[Any],
    deferred: list[Any] | None = None,
    *,
    sandboxed: frozenset[str] | None = None,
    tool_name: Callable[[Any], str],
) -> list[Any]:
    """Turn (base, deferred) tool lists into the toolsets ``Agent(toolsets=…)`` takes.

    Args:
        base: tools visible to the model from turn 1.
        deferred: tools hidden until the model searches for them. Omitted or empty
            → a single toolset is returned.
        sandboxed: names of the (read-only) tools ``CodeMode`` will expose inside
            ``run_code``. These are swapped for their sandbox projection.
        tool_name: how to read a tool's name — host-supplied, because a "tool" here
            may be a bare callable, a pydantic-ai ``Tool``, or a host wrapper.

    Returns:
        ``[FunctionToolset(base)]``, plus ``FunctionToolset(deferred,
        defer_loading=True)`` when there are deferred tools. Empty list on failure:
        a broken tool must not take down the whole agent.
    """
    from pydantic_ai.toolsets import FunctionToolset

    try:
        from modules.django_llm.agent.tools.core import get_sandbox_callable

        projected = base
        if sandboxed:
            projected = [
                _to_sandbox(tool, sandboxed, get_sandbox_callable, tool_name)
                for tool in base
            ]

        result: list[Any] = [FunctionToolset(projected)]
        if deferred:
            result.append(FunctionToolset(deferred, defer_loading=True))
        return result
    except Exception:
        logger.exception("[toolsets] could not build toolsets — agent will run toolless")
        return []


def _to_sandbox(tool: Any, sandboxed: frozenset[str], get_sandbox, tool_name) -> Any:
    """Swap a tool for its sandbox projection when ``CodeMode`` will run it.

    Returns the tool untouched when it is not sandboxed, or when it has no
    projection — a plain ``@llm_tool`` callable with no ``BaseTool`` behind it has no
    structured surface to return, so it stays on the native path rather than feeding
    model code a string it cannot index.
    """
    if tool_name(tool) not in sandboxed:
        return tool
    projection = get_sandbox(getattr(tool, "function", tool))
    return projection if projection is not None else tool
