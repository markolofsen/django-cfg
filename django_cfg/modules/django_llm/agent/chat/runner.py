"""One answer of a chat kind as a stream of widget-wire events.

`kind_source` builds the pydantic-ai agent from a `ChatKind` and its deps (instructions, tools, token cap) and drives
`stream_agent_run` on the widget wire with the kind's limits, payload kinds and tool-output cap. It stores nothing: hand
the source to `RunDriver` (ping, wall-clock cap, shielded finalize) or to `ChatService.frames`, which also persists.

Tool calls and results are consumed here and never leave: a client sees phases, text and the payload kinds the kind
declares. The calls are captured in `out.tool_calls` for the host to store and replay.
"""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator, Sequence
from contextlib import aclosing
from typing import Any

from pydantic_ai import Agent
from pydantic_ai.models import Model

from django_cfg.modules.django_llm.agent.bus.events import (
    DoneEvent,
    ErrorEvent,
    SSEEvent,
    TextDeltaEvent,
    UIPayloadEvent,
)
from django_cfg.modules.django_llm.agent.capabilities import lenient_json_args_capability, tool_guard_capability
from django_cfg.modules.django_llm.agent.chat.compaction import compactor, soft_cap
from django_cfg.modules.django_llm.agent.chat.kind import ChatKind
from django_cfg.modules.django_llm.agent.chat.turn import StoredMessage
from django_cfg.modules.django_llm.agent.runtime.cost import Pricer
from django_cfg.modules.django_llm.agent.runtime.errors import DEFAULT_ERROR_MESSAGES
from django_cfg.modules.django_llm.agent.runtime.limits import RunLimits
from django_cfg.modules.django_llm.agent.runtime.streaming import coerce_payloads
from django_cfg.modules.django_llm.agent.trace.capability import TraceCapability
from django_cfg.modules.django_llm.agent.trace.recorder import Recorder

log = logging.getLogger(__name__)


def _tool_name(tool: Any) -> str:
    return getattr(tool, "name", None) or getattr(tool, "__name__", "")


def tool_timeouts(tools: Sequence[Any]) -> dict[str, float]:
    """`{name: seconds}` for the tools that carry a `ToolMeta` (`@llm_tool`, `BaseTool`); the rest get `KindLimits.tool_timeout_s`."""
    from django_cfg.modules.django_llm.agent.tools.core import get_tool_meta

    found: dict[str, float] = {}
    for tool in tools:
        meta = get_tool_meta(getattr(tool, "function", tool))
        if meta is not None:
            found[_tool_name(tool)] = meta.resolved_timeout()
    return found


def tool_categories(tools: Sequence[Any]) -> dict[str, str]:
    """`{name: ToolMeta.category}` for the tools that carry a `ToolMeta`: the default role of their trace step."""
    from django_cfg.modules.django_llm.agent.tools.core import get_tool_meta

    found: dict[str, str] = {}
    for tool in tools:
        meta = get_tool_meta(getattr(tool, "function", tool))
        if meta is not None:
            found[_tool_name(tool)] = str(meta.category)
    return found


def build_model(chain: tuple[str, ...]) -> Model:
    """The real model for a chain of slugs: the first, with the rest as fall-over (API errors and malformed bodies)."""
    from django_cfg.modules.django_llm.agent.runtime.model_builder import build_fallback_model

    return build_fallback_model(chain[0], tuple(chain[1:]))


async def kind_source(
    kind: ChatKind,
    deps: Any,
    history: list[dict],
    prompt: "str | list[Any]",  # the user's text, or the text and its file parts (`attachments.delivery`)
    *,
    model: Model,
    out: Any = None,
    pricer: Pricer | None = None,
    price_timeout_s: float = 3.0,
    trace: "Recorder | None" = None,
) -> AsyncIterator[SSEEvent]:
    """Events of one answer, ending in exactly one `DoneEvent` or `ErrorEvent`.

    `history` is `[{role, content, tool_calls?}]` (what `ChatService.history_for_model` returns). `out` is a
    `StreamRunResult` the caller keeps to read `out.tool_calls` afterwards. `trace` is the answer's `Recorder` (the service makes
    one when `kind.trace_level > 0`): its capability sits outside the tool guard, so a timeout is a step too.
    """
    from django_cfg.modules.django_llm.agent.runtime.history import convert_history
    from django_cfg.modules.django_llm.agent.runtime.streaming import StreamRunResult, stream_agent_run

    out = out if out is not None else StreamRunResult()
    limits = kind.limits
    try:
        from pydantic_ai.capabilities import PrepareTools, ProcessHistory

        extra: dict[str, Any] = {}
        caps: list[Any] = []
        instructions = kind.build_instructions(deps)
        tools = list(kind.build_tools(deps))
        kb = None
        if kind.knowledge is not None and kind.knowledge is not False:
            from django_cfg.modules.django_llm.agent.chat import knowledge as kb_mod

            kb = kb_mod.runtime(kind.knowledge, deps)
        if kb is not None:
            clash = sorted({_tool_name(t) for t in tools} & set(kb.tool_names()))
            if clash:
                raise ValueError(
                    f"chat kind {kind.name!r}: the kind's own tool(s) {', '.join(clash)} have the same name as the knowledge base's; "
                    f"set knowledge=Knowledge(tool_prefix='library_') (any other prefix) or rename the kind's tool"
                )
            instructions = f"{instructions}\n\n{kb.prompt}"  # the tree comes after the kind's own text: stable bytes, cache-friendly
            tools += kb.tools
        if limits.tool_calls_soft is not None:
            caps.append(PrepareTools(soft_cap(limits.tool_calls_soft)))
        keep = limits.keep_tool_results
        if keep is None and kb is not None:
            keep = kb.session.caps.keep_tool_results  # a kind's own setting wins over the knowledge base's
        if keep is not None or limits.tool_result_chars is not None:
            caps.append(ProcessHistory(compactor(keep, limits.tool_result_chars)))
        guard = tool_guard_capability(timeouts=tool_timeouts(tools), default_timeout_s=limits.tool_timeout_s)
        if trace is not None and trace.level > 0:
            declared = {**(kb.trace_tools() if kb is not None else {}), **(kind.trace_tools or {})}
            caps[:0] = [lenient_json_args_capability(), TraceCapability(trace, declared, tool_categories(tools)), guard]
        else:
            caps[:0] = [lenient_json_args_capability(), guard]
        if kind.capabilities is not None:
            caps.extend(kind.capabilities(deps))
        extra["capabilities"] = caps
        extra["retries"] = kind.retries
        agent = Agent(
            model,
            deps_type=type(deps),
            instructions=instructions,
            tools=tools,
            model_settings={**(limits.model_settings or {}), "max_tokens": limits.max_tokens},
            **extra,
        )
    except Exception:  # noqa: BLE001 - the stream ends with one `error` frame; the cause goes to the log
        log.exception("chat: could not build the %s agent", kind.name)
        yield ErrorEvent(error=DEFAULT_ERROR_MESSAGES["failed"], code="failed")
        return
    after_tool = None
    if kind.after_tool is not None:
        hook = kind.after_tool
        after_tool = lambda name, result: hook(deps, name, result)  # noqa: E731
    source = stream_agent_run(
        agent=agent,
        deps=deps,
        user_message=prompt,
        message_history=convert_history(history),
        deferred_tool_results=None,
        is_admin_chat=False,
        out=out,
        log_prefix=f"chat:{kind.name}",
        wire="widget",
        limits=RunLimits(request_limit=limits.request_limit, tool_calls_limit=limits.tool_calls_limit),
        payload_kinds=kind.payload_kinds,
        phase_for_tool=kind.phase_for_tool,
        emit_reasoning=kind.stream_reasoning,
        require_answer=True,
        tool_output_chars=limits.tool_output_chars,
        pricer=pricer,
        price_timeout_s=price_timeout_s,
        after_tool=after_tool,
    )
    said: list[str] = []
    async with aclosing(source):
        async for event in source:
            if isinstance(event, TextDeltaEvent):
                said.append(event.delta)
            elif isinstance(event, DoneEvent):
                if kb is not None and (note := kb.note_for("".join(said))):
                    log.warning("chat:%s: answer cites a knowledge file it did not open", kind.name)
                    said.append(note)
                    yield TextDeltaEvent(delta=note)
                if kind.closing_payloads is not None:
                    for closing in _closing(kind, deps, "".join(said)):
                        yield closing
            yield event


def _closing(kind: ChatKind, deps: Any, text: str) -> list[UIPayloadEvent]:
    """The kind's `closing_payloads` for the finished text, held to `payload_kinds`. A failing hook costs the extras, never the answer."""
    try:
        pairs = coerce_payloads(kind.closing_payloads(deps, text))
    except Exception:  # noqa: BLE001
        log.exception("chat:%s: closing_payloads failed", kind.name)
        return []
    out: list[UIPayloadEvent] = []
    for payload_kind, data in pairs:
        if payload_kind not in kind.payload_kinds:
            log.warning("chat:%s: closing payload of undeclared kind %r dropped", kind.name, payload_kind)
            continue
        out.append(UIPayloadEvent(kind=payload_kind, data=data))
    return out


def replay_events(answer: StoredMessage) -> list[SSEEvent]:
    """The events that replay a stored `done` answer: its text, its payloads, then `done` with `replayed`."""
    out: list[SSEEvent] = []
    if answer.text:
        out.append(TextDeltaEvent(delta=answer.text))
    out.extend(UIPayloadEvent(kind=p["kind"], data=p["data"]) for p in answer.parts)
    out.append(
        DoneEvent(
            tokens_input=answer.tokens_in,
            tokens_output=answer.tokens_out,
            cost_usd=float(answer.cost_usd or 0),
            finish_reason="stop",
            replayed=True,
        )
    )
    return out
