"""Per-turn call-cap capability.

A ``prepare_tools`` hook that drops a tool from the model surface once
its per-turn call count is hit. A tool *result* ("stop calling me")
cannot reliably stop a model — only removing the tool from the request
can. This is the hard backstop against tight re-call loops by weak
models.
"""

from __future__ import annotations

import logging
from typing import Any

from pydantic_ai import RunContext
from pydantic_ai.capabilities import Hooks
from pydantic_ai.tools import ToolDefinition

logger = logging.getLogger(__name__)


# Per-tool overrides. A tool named here gets its own cap instead of the
# default below.
_PER_TURN_CALL_CAPS: dict[str, int] = {
    "point_at_elements": 3,
}

# Tools that carry no cap at all, by name.
#
# ``run_code`` is not a read tool that happens to be uncapped — it is **the read
# surface**. Every CRM read now lives inside it, so a cap on ``run_code`` is a cap
# on how many times the agent may look at anything, for the whole turn.
#
# It was capped at 3 by omission (the default below catches unknown names), and a
# live group run showed the cost: ``sprint_cleanup`` archived 2 of 4 tasks and
# stopped, ``client_task_audit`` got one ``run_code``, spent it, and had no way to
# read again — so it did nothing. Every one of them passed when run alone, because
# alone they happened to need fewer reads.
#
# That looked like flakiness. It was a budget.
#
# Capping ``run_code`` also inverts the loop guard's own logic. The pathology it
# exists to stop is a model hammering a tool that *cannot answer* the question,
# because the tool that can is hidden. ``run_code`` is the tool that can. A turn
# that calls it five times is a turn doing a five-step job — read, write, re-read,
# write, confirm — not a turn stuck in a loop.
#
# Two real backstops remain, and both are stronger than a per-tool call count:
# ``UsageLimits(request_limit=15)`` bounds the model round-trips in a turn
# (``agent.py`` / ``runtime/streaming.py``), and
# ``CodeMode``'s ``resource_limits['max_duration_secs']`` bounds each single execution.
# (``ChatAgentDeps.max_tool_calls`` is *not* one of them — despite the name, it
# only feeds ``AgentSearchContext.can_search``, which gates the RAG path, not the
# tool loop.)
_UNCAPPED_TOOLS = frozenset({
    "run_code",
    # Tool discovery. Capping it strands the model behind a toolset it cannot see.
    "search_tools",
})

# The cap every other read tool gets.
#
# This used to be unset, so the dict above was the *whole* guard: exactly one
# tool out of a hundred was protected, and a loop on any other ran free. A live
# e2e run found it — asked to triage overdue tasks, the model called
# ``list_documents`` **41 times in a row**, touched no task, and the "hard
# backstop against tight re-call loops" watched it happen.
#
# 3, not 6. The first live run capped at 6 and the model still lost: it burned 6
# calls on `list_documents`, 6 on `list_staff`, 6 on `list_message_attachments` --
# 18 of its 15-call budget on tools that could not answer the question -- before it
# found `run_code`. Capping the loop is not enough; it has to be cut early enough
# that the turn survives it.
#
# A legitimate turn re-reads a tool once or twice (paging, a retry after a bad
# argument). Nothing legitimate reads the same thing a third time and keeps going.
_DEFAULT_READ_CAP = 3

# Categories that are never capped.
#
# Dropping a mutation mid-turn is worse than the loop it would prevent: the model
# has already told the operator it is about to close the ticket, and the tool that
# does it vanishes from under it. Loops are a read-side pathology anyway — a model
# spins because it cannot find something, not because it keeps writing.
_UNCAPPED_CATEGORIES = frozenset({
    "mutation",
    "outbound_propose",
    "outbound_confirm",
    "outbound_cancel",
    "conversation",
})


def _categories_for(deps: Any) -> dict[str, str]:
    """Map tool name -> ``ToolMeta.category`` for the tools *this* run has.

    ``prepare_tools`` sees ``ToolDefinition``s, which carry the name but not our
    ``ToolMeta``, so the category has to be looked up. It is resolved from the
    run's own ``deps`` rather than a module-level table: the registry needs deps to
    decide which tools exist at all, and faking one silently yields an empty map —
    which would classify **every** tool as ``read`` and start capping mutations.
    Cached on the deps object, so it is built once per run, not once per request.
    """
    cached = getattr(deps, "_cmdop_tool_categories", None)
    if cached is not None:
        return cached

    from modules.django_llm.agent.tools.core import get_tool_meta

    # The tools come from the host, through the `ToolProvider` seam on deps — the
    # harness must not know a registry exists, let alone whose. See
    # `agent/protocols.py`.
    provider = getattr(deps, "tool_provider", None)
    if provider is None:
        # NOT a silently-empty map. An empty map classifies every tool as `read`,
        # which switches the mutation cap off — the guard would appear to work while
        # protecting nothing. A missing provider is a wiring bug, and it says so.
        logger.error(
            "[capability] deps has no `tool_provider` — cannot resolve tool "
            "categories, so the per-turn mutation cap is INACTIVE for this run. "
            "The host must supply a ToolProvider (see agent/protocols.py)."
        )
        return {}

    built: dict[str, str] = {}
    try:
        for tool in provider.get_tools():
            fn = getattr(tool, "function", tool)
            meta = get_tool_meta(fn)
            if meta is not None:
                built[getattr(fn, "__name__", "")] = meta.category
    except Exception:
        logger.exception("[capability] could not resolve tool categories — capping reads only")

    try:
        deps._cmdop_tool_categories = built
    except Exception:  # frozen deps: rebuild each request rather than fail
        pass
    return built


def per_turn_call_cap_capability() -> Hooks[Any]:
    """Drop a tool from the model surface once its per-turn call cap is hit.

    ``prepare_tools`` runs before every model request inside a run. Once a
    capped tool's per-turn count (tracked on ``ChatAgentDeps``) reaches its
    limit, this hook removes its ``ToolDefinition`` so the next request does
    not list it — the model then physically cannot call it again and is
    forced to reply in prose. This is the hard stop that the tool-result
    note alone could never guarantee.
    """

    def _cap_for(name: str, categories: dict[str, str]) -> int | None:
        """The per-turn cap for ``name``, or ``None`` when it is uncapped.

        A name we do not recognise still gets the read cap — an unknown tool is
        one a loop could hammer. But the two capability-injected tools we *do*
        know about (``run_code``, ``search_tools``) are named explicitly in
        ``_UNCAPPED_TOOLS``, because falling through to the read cap is exactly
        the bug that comment used to describe as "the safe side".
        """
        if name in _UNCAPPED_TOOLS:
            return None
        explicit = _PER_TURN_CALL_CAPS.get(name)
        if explicit is not None:
            return explicit
        if categories.get(name, "read") in _UNCAPPED_CATEGORIES:
            return None
        return _DEFAULT_READ_CAP

    def _prepare(
        ctx: RunContext[Any], tool_defs: list[ToolDefinition], /,
    ) -> list[ToolDefinition]:
        counter = getattr(ctx.deps, "tool_call_count", None)
        if not callable(counter):
            return tool_defs

        categories = _categories_for(ctx.deps)

        kept: list[ToolDefinition] = []
        for td in tool_defs:
            name = getattr(td, "name", "") or ""
            cap = _cap_for(name, categories)
            if cap is not None and counter(name) >= cap:
                logger.warning(
                    "[capability] per-turn cap hit — dropping tool=%s (calls=%d, cap=%d). "
                    "The model is looping; it must now answer in prose.",
                    name, counter(name), cap,
                )
                continue
            kept.append(td)
        return kept

    async def _count(
        ctx: RunContext[Any],
        *,
        call: Any,
        tool_def: ToolDefinition,
        args: Any,
    ) -> Any:
        """Count every tool call, so ``_prepare`` has something to act on.

        **Nothing was doing this.** ``ChatAgentDeps.bump_tool_call`` existed and had
        exactly one caller: ``point_at_elements``, bumping *itself* from inside its
        own body. Every other tool's count stayed at zero forever, so
        ``counter(name) >= cap`` was never true and the "hard backstop against tight
        re-call loops" only ever protected the one tool that had opted in by hand.

        A live e2e run is what exposed it: the model called ``list_documents`` 41
        times in a row and nothing stopped it.
        """
        bump = getattr(ctx.deps, "bump_tool_call", None)
        if callable(bump):
            bump(getattr(tool_def, "name", "") or "")
        return args

    hooks: Hooks[Any] = Hooks(
        prepare_tools=_prepare,
        before_tool_execute=_count,
    )
    return hooks
