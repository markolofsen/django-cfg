"""Pydantic-AI ``Agent.run_stream_events`` → SSE event adapter.

Reusable streaming loop. The main ``ChatAgent`` and Plan-32's
``OnboardingAgent`` both feed their pre-built ``Agent`` here and get
back the same SSE event stream — text deltas, tool-call breadcrumbs,
approval-required cards, the final ``DoneEvent``.

Why isolated from ``ChatAgent``: the streaming plumbing is ~200 LoC of
ceremony around pydantic-ai's internals — none of it is specific to admin
chat. Pulling it out lets the onboarding interviewer agent use the same
battle-tested loop with its own prompt + tools, without copy-pasting.

Implementation note — why ``run_stream_events`` instead of ``run_stream``:
  ``run_stream`` only fires ``event_stream_handler`` during the model
  response node; tool execution (``CallToolsNode``) runs *after* the
  stream closes in ``on_complete()``, so ``FunctionToolCallEvent`` /
  ``FunctionToolResultEvent`` are never emitted through the handler.
  ``run_stream_events`` wraps ``agent.run()`` with an ``event_stream_handler``
  that fires for *every* node, then pipes all events through an anyio
  memory stream — giving us text deltas AND tool events in a single loop.
"""

from __future__ import annotations

import json
import logging
import time
from collections.abc import Iterable, Iterator
from typing import Any, AsyncIterator

from pydantic_ai import Agent, DeferredToolRequests, DeferredToolResults
from pydantic_ai.messages import (
    FunctionToolCallEvent,
    FunctionToolResultEvent,
    ModelMessage,
    PartDeltaEvent,
    PartStartEvent,
    TextPart,
    TextPartDelta,
    ToolReturnPart as _ToolReturnPart,
)
from pydantic_ai.run import AgentRunResultEvent

from modules.django_llm.agent.tools.core._base_tool import strip_raw
from modules.django_llm.agent.capabilities.code_mode import (
    iter_sandboxed_calls,
)
from modules.django_llm.agent.runtime.action_guard import (
    claims_action_without_evidence,
    tool_return_succeeded,
)
from modules.django_llm.agent.bus.events import (
    ApprovalRequiredEvent,
    DirectiveEvent,
    DoneEvent,
    ErrorEvent,
    SSEEvent,
    TextDeltaEvent,
    ToolCallEvent,
    ToolResultEvent,
    UIPayloadEvent,
)
from modules.django_llm.agent.runtime.ui_payloads import (
    UI_PAYLOAD_TYPES,
    DirectivePayload,
)

logger = logging.getLogger(__name__)


def _format_user_error(exc: Exception) -> str:
    """Map pydantic-ai / network exceptions to short customer-facing text.

    The full traceback still goes to logs via ``logger.exception`` —
    this only shapes what reaches the SSE stream and ends up rendered
    as a chat error bubble.
    """
    name = type(exc).__name__
    msg = str(exc)
    if "Exceeded maximum output retries" in msg or name == "UnexpectedModelBehavior":
        return "The assistant got stuck mid-thought. Please try rephrasing or send the message again."
    if "ModelHTTPError" in name or "status_code" in msg:
        return "The model service is temporarily unavailable. Please try again in a moment."
    if "TimeoutError" in name or "timeout" in msg.lower():
        return "The model took too long to respond. Please try again."
    if "tool_choice" in msg:
        return "Model configuration mismatch. Please notify support."
    return "Something went wrong while generating the reply. Please try again."


def _iter_ui_payloads(part: Any) -> Iterator[Any]:
    """Yield typed UI payload models from a ``ToolReturnPart.metadata``.

    Supports three shapes (matching the pattern in pydantic-ai's
    Vercel adapter ``iter_metadata_chunks``):
      - metadata is a single ``UIPayload`` instance (most common)
      - metadata is an iterable of them (multi-widget turn — rare)
      - anything else: skip silently

    The runtime calls this for every ``FunctionToolResultEvent``;
    tools that don't drive a widget simply yield nothing.
    """
    meta = getattr(part, "metadata", None)
    if meta is None:
        return
    if isinstance(meta, UI_PAYLOAD_TYPES):
        yield meta
        return
    if isinstance(meta, (str, bytes)):
        return
    if isinstance(meta, Iterable):
        for item in meta:
            if isinstance(item, UI_PAYLOAD_TYPES):
                yield item


def _iter_directive_payloads(part: Any) -> Iterator[DirectivePayload]:
    """Yield ``DirectivePayload`` models from a ``ToolReturnPart.metadata``.

    Mirrors ``_iter_ui_payloads`` exactly — same single / iterable / skip
    shapes — but for the directive side channel. The ``point_at_elements``
    tool attaches a ``DirectivePayload`` to its return metadata; the
    runtime drains it here and emits a ``DirectiveEvent``.

    Replaces the old reply-text regex scan: directives now arrive as
    schema-validated tool args, never as parsed prose, so a malformed
    model output can no longer corrupt — or poison the history of — the
    highlight feature.
    """
    meta = getattr(part, "metadata", None)
    if meta is None:
        return
    if isinstance(meta, DirectivePayload):
        yield meta
        return
    if isinstance(meta, (str, bytes)):
        return
    if isinstance(meta, Iterable):
        for item in meta:
            if isinstance(item, DirectivePayload):
                yield item


def _make_tool_result_event(tool_name: str, result_repr: str) -> ToolResultEvent:
    """Build a ToolResultEvent, extracting structured frontend data from result_repr.

    How data reaches here:
      BaseTool._execute() encodes the raw dict into the return string via
      _embed_raw("<llm_text>\\x00RAW\\x00{json}"). pydantic-ai stores this
      as the tool-return content (FunctionToolResultEvent / ToolReturnPart).
      strip_raw() splits the sentinel, giving us both the clean LLM text
      (truncated to 500 chars) and the structured dict for the frontend.
    """
    clean_text, raw_data = strip_raw(result_repr)
    return ToolResultEvent(tool=tool_name, result=clean_text[:500], data=raw_data)


class StreamRunResult:
    """Side-channel returned via attribute mutation on the stream owner.

    Not yielded — the caller (e.g. ``ChatAgent``) reads it after the
    iterator drains so the chat-store hook can persist
    ``last_messages_json`` for the HITL resume endpoint.
    """

    def __init__(self) -> None:
        self.last_deferred: DeferredToolRequests | None = None
        self.last_messages_json: str = ""


async def stream_agent_run(
    *,
    agent: Agent,
    deps: Any,
    user_message: str | None,
    message_history: list[ModelMessage],
    deferred_tool_results: DeferredToolResults | None,
    is_admin_chat: bool,
    out: StreamRunResult,
    log_prefix: str = "Agent",
) -> AsyncIterator[SSEEvent]:
    """Drive a pydantic-ai Agent via run_stream_events and yield SSE events.

    Uses ``agent.run_stream_events()`` which internally calls ``agent.run()``
    with an ``event_stream_handler`` wired to every graph node — including
    ``CallToolsNode``. This means ``FunctionToolCallEvent`` and
    ``FunctionToolResultEvent`` arrive in the same stream as text deltas,
    solving the "tool events never reach browser" problem that occurred with
    ``run_stream`` + manual queue draining.

    On a deferred run-end emits a single ``ApprovalRequiredEvent`` per
    pending tool_call_id, then closes the stream cleanly without
    ``DoneEvent``. The chat-store hook in views.py persists the run's
    ``all_messages_json()`` for the resume endpoint via ``out``.
    """

    total_tokens: int | None = None
    run_cost = None  # RunCost for the turn, set when the run completes
    text_buf: list[str] = []
    tool_call_count = 0
    model_turn = 0
    seen_tool_call_ids: set[str] = set()
    seen_tool_return_ids: set[str] = set()
    # Mutation tools that returned a SUCCESS this run — Layer 3 evidence.
    successful_tools: set[str] = set()
    # Every tool the model invoked this run, in call order. Layer 3 needs
    # both lists to fire only when an attempted mutation didn't succeed.
    called_tools: list[str] = []
    t0 = time.monotonic()

    # ─── Tool-event visibility ────────────────────────────────────────────
    #
    # `tool_call` / `tool_result` SSE frames carry the raw tool name, the
    # arguments the model invented, and the full tool return value. For the
    # admin chat that's a useful debug trace — operators want to see *why*
    # the assistant answered the way it did. For the **public chat** it is
    # a leak surface:
    #   - Tool names disclose product internals (`get_my_profile`,
    #     `calculate_tax`, `search_vehicles`) — an attacker probing the
    #     endpoint learns the agent's tool surface for free.
    #   - Tool results often carry auth / profile data, internal IDs,
    #     and provider-specific error strings the user never sees in the
    #     rendered answer.
    #   - Hiding events client-side via a React prop is not a fix — curl
    #     and DevTools see the raw frames. The only honest defence is to
    #     never send them in the first place.
    #
    # Product widgets (vehicle cards, tax tables) do NOT depend on this
    # gate — they ride the `ui_payload` SSE channel which is drained from
    # `ToolReturnPart.metadata` and always emitted (see _iter_ui_payloads
    # below). That means tightening the gate has no UX consequences on
    # public-prod: cards still render, tool surface stays hidden.
    #
    # Rule: emit raw tool events only for admin sessions. Whether a non-admin run may
    # see them is HOST policy (CRM exposes an env escape hatch for reproducing a bug
    # against the public-chat transport) — so the harness asks deps rather than
    # reading a CRM config module from inside its own loop.
    expose_tool_events = bool(getattr(deps, "expose_tool_events", is_admin_chat))

    try:
        from pydantic_ai import UsageLimits
        _limits = UsageLimits(request_limit=15)
    except Exception:
        _limits = None

    run_kwargs: dict = {
        "deps": deps,
        "message_history": message_history,
    }
    if deferred_tool_results is not None:
        run_kwargs["deferred_tool_results"] = deferred_tool_results
    if _limits is not None:
        run_kwargs["usage_limits"] = _limits

    run_args: tuple = () if user_message is None else (user_message,)

    try:
        # pydantic-ai 2.x returns an async context manager rather than a bare
        # iterator: entering it owns the background run task, so it is cancelled
        # deterministically when the consumer stops iterating early — which an SSE
        # response does every time the browser disconnects mid-answer.
        async with agent.run_stream_events(*run_args, **run_kwargs) as event_stream:
            async for event in event_stream:

                # ── First text chunk of a part ──────────────────────────────────
                # pydantic-ai emits PartStartEvent(TextPart(content=...)) for the
                # very first text chunk of each model turn, then PartDeltaEvent
                # for subsequent deltas. Without this branch the opening tokens
                # of every reply are dropped, so users see answers that start
                # mid-sentence.
                if isinstance(event, PartStartEvent) and isinstance(event.part, TextPart):
                    delta = event.part.content
                    if delta:
                        if not text_buf:
                            model_turn += 1
                            logger.info(
                                "[%s] model_turn=%d  tool_calls_so_far=%d",
                                log_prefix, model_turn, tool_call_count,
                            )
                        text_buf.append(delta)
                        yield TextDeltaEvent(delta=delta)

                # ── Text delta (continuation of an open text part) ──────────────
                elif isinstance(event, PartDeltaEvent) and isinstance(event.delta, TextPartDelta):
                    delta = event.delta.content_delta
                    if delta:
                        if not text_buf:
                            model_turn += 1
                            logger.info(
                                "[%s] model_turn=%d  tool_calls_so_far=%d",
                                log_prefix, model_turn, tool_call_count,
                            )
                        text_buf.append(delta)
                        yield TextDeltaEvent(delta=delta)

                # ── Tool call announced ─────────────────────────────────────────
                elif isinstance(event, FunctionToolCallEvent):
                    cid = str(event.part.tool_call_id or "")
                    if cid in seen_tool_call_ids:
                        continue
                    seen_tool_call_ids.add(cid)
                    raw_args = event.part.args
                    if isinstance(raw_args, str):
                        args_repr = raw_args
                    elif raw_args is not None:
                        args_repr = str(raw_args)
                    else:
                        args_repr = ""
                    tool_call_count += 1
                    called_tools.append(event.part.tool_name)
                    logger.info(
                        "[%s] tool_call #%d  name=%s  args=%s",
                        log_prefix, tool_call_count,
                        event.part.tool_name, args_repr[:300],
                    )
                    # Tool name + args leak agent internals — gated to admin/dev.
                    if expose_tool_events:
                        yield ToolCallEvent(tool=event.part.tool_name, args=args_repr)

                # ── Tool result received ────────────────────────────────────────
                elif isinstance(event, FunctionToolResultEvent):
                    # pydantic-ai 2.x renamed the payload to ``part`` (it was
                    # ``result`` in 1.x) — reading the old name silently yields
                    # no tool results at all, so the UI shows a call that never
                    # completes.
                    cid = str(event.part.tool_call_id or "")
                    if cid and cid in seen_tool_return_ids:
                        continue
                    if cid:
                        seen_tool_return_ids.add(cid)

                    result_part = event.part
                    if not isinstance(result_part, _ToolReturnPart):
                        # RetryPromptPart — skip, not a successful result
                        continue

                    result_repr = str(result_part.content) if result_part.content is not None else ""
                    if "Tool not executed" in result_repr:
                        continue

                    tool_name = result_part.tool_name
                    logger.info(
                        "[%s] tool_result  name=%s  len=%d  preview=%r",
                        log_prefix, tool_name, len(result_repr), result_repr[:200],
                    )

                    # Layer 3 evidence: record tools whose return was a success
                    # (not a ToolError) so the end-of-stream gate can tell a real
                    # action from a fabricated "sent".
                    if tool_return_succeeded(result_part.content):
                        successful_tools.add(tool_name)

                    # ── Sandboxed calls (CodeMode) ──────────────────────────────
                    # ``run_code`` ran N tools inside Monty, so no native call/result
                    # event fired for any of them. Replay them here from the metadata
                    # the harness attached, so the admin UI's tool bubbles, the
                    # persisted ``ChatMessage.tool_calls`` and the Layer-3 evidence
                    # set all behave exactly as they do on the native path.
                    for inner_name, inner_args, inner_return in iter_sandboxed_calls(result_part):
                        if not inner_name:
                            continue
                        tool_call_count += 1
                        called_tools.append(inner_name)
                        logger.info(
                            "[%s] tool_call #%d  name=%s  args=%s  (sandboxed)",
                            log_prefix, tool_call_count, inner_name, inner_args[:300],
                        )
                        if expose_tool_events:
                            yield ToolCallEvent(tool=inner_name, args=inner_args)

                        if inner_return is None:
                            continue
                        inner_content = getattr(inner_return, "content", None)
                        if tool_return_succeeded(inner_content):
                            successful_tools.add(inner_name)
                        if expose_tool_events:
                            yield _make_tool_result_event(
                                inner_name,
                                str(inner_content) if inner_content is not None else "",
                            )

                    # UI side channel — drain typed widget payloads from
                    # ToolReturnPart.metadata and emit them as `ui_payload`
                    # SSE frames. Always emitted, independent of the
                    # tool-event gate below: the tool surface (name + raw
                    # args + raw result) is a debug aid; the UI payload is
                    # a product feature carrying only what the widget
                    # needs. Mirrors pydantic-ai's own UI adapter pattern
                    # (see ui/vercel_ai/_utils.py:iter_metadata_chunks).
                    for ui_payload in _iter_ui_payloads(result_part):
                        logger.info(
                            "[%s] ui_payload  kind=%s",
                            log_prefix, ui_payload.kind,
                        )
                        yield UIPayloadEvent(
                            kind=ui_payload.kind,
                            data=ui_payload.model_dump(exclude={"kind"}),
                        )

                    # Directive side channel — drain `point` directives the
                    # point_at_elements tool attached to its return metadata
                    # and emit them as `directive` SSE frames. Same plumbing
                    # as the UI payloads above; always emitted, independent
                    # of the tool-event gate. The wire shape is identical to
                    # the old regex path, so the frontend overlay is unchanged.
                    for directive_payload in _iter_directive_payloads(result_part):
                        if directive_payload.directives:
                            logger.info(
                                "[%s] directive  count=%d",
                                log_prefix, len(directive_payload.directives),
                            )
                            yield DirectiveEvent(
                                directives=directive_payload.directives,
                            )

                    # Tool returns often carry auth / profile data — gated.
                    if expose_tool_events:
                        yield _make_tool_result_event(tool_name, result_repr)

                # ── Run complete ────────────────────────────────────────────────
                elif isinstance(event, AgentRunResultEvent):
                    run_result = event.result

                    # Collect usage + price the run. `AgentRunResult.usage` is a
                    # property (a `RunUsage` with the input/output split); the model
                    # slug that actually served the run is `.response.model_name`
                    # (which, through a FallbackModel, is the model that *won*, not
                    # necessarily the primary). Pricing never raises — cost is
                    # telemetry, not the answer; see runtime/cost.py.
                    try:
                        from modules.django_llm.agent.runtime.cost import price_run

                        usage_obj = run_result.usage
                        model_slug = str(
                            getattr(getattr(run_result, "response", None), "model_name", "") or ""
                        )
                        run_cost = price_run(usage_obj, model_slug)
                        total_tokens = run_cost.total_tokens or None
                    except Exception:
                        logger.exception("[stream] usage/cost collection failed")

                    # Handle deferred / HITL approval
                    output = run_result.output
                    if isinstance(output, DeferredToolRequests):
                        out.last_deferred = output
                        try:
                            out.last_messages_json = run_result.all_messages_json().decode()
                        except Exception:
                            out.last_messages_json = ""

                        for call in output.approvals:
                            cid = str(getattr(call, "tool_call_id", "") or "")
                            raw_args = getattr(call, "args", None)
                            args_payload: Any
                            if isinstance(raw_args, str) and raw_args.strip():
                                try:
                                    args_payload = json.loads(raw_args)
                                except json.JSONDecodeError:
                                    args_payload = raw_args
                            elif raw_args is not None:
                                args_payload = raw_args
                            else:
                                args_payload = {}

                            if cid and cid in seen_tool_call_ids and cid not in seen_tool_return_ids:
                                seen_tool_return_ids.add(cid)
                                yield ToolResultEvent(
                                    tool=call.tool_name,
                                    result="(awaiting approval)",
                                )
                            logger.info(
                                "[%s] approval_required  tool=%s  call_id=%s",
                                log_prefix, call.tool_name, cid,
                            )
                            yield ApprovalRequiredEvent(
                                tool_call_id=cid,
                                tool=call.tool_name,
                                args=args_payload,
                            )
                        # No DoneEvent for deferred runs
                        return

                    else:
                        out.last_deferred = None
                        out.last_messages_json = ""

    except Exception as exc:
        logger.exception("[%s] stream error: %s", log_prefix, exc)
        yield ErrorEvent(error=_format_user_error(exc))
        return

    elapsed = round((time.monotonic() - t0) * 1000)
    text_len = sum(len(c) for c in text_buf)
    search_ctx = getattr(deps, "search_ctx", None)
    searches_used = len(search_ctx.searches) if search_ctx else 0

    logger.info(
        "[%s] done  tokens=%s  model_turns=%d  tool_calls=%d  searches=%d  text_len=%d  elapsed_ms=%d",
        log_prefix, total_tokens, model_turn, tool_call_count,
        searches_used, text_len, elapsed,
    )

    # UI directives are emitted inline by the point_at_elements tool via
    # the directive side channel (see _iter_directive_payloads above) —
    # no end-of-stream reply scan, no regex, no JSON parsing of prose.

    # Layer 3 anti-hallucination gate (admin chat only): if the assistant
    # claimed a completed action but no mutation tool succeeded this run,
    # surface an explicit error instead of letting the fabricated success
    # stand. Runs after the model is done — cannot be bypassed by it.
    policy = getattr(deps, "action_guard_policy", None)
    if is_admin_chat and policy is not None:
        # The guard is the harness's; the evidence and the correction text are the
        # host's — reached through the `ActionGuardPolicy` seam so this loop does not
        # import CRM. The reply is the policy's, NOT a string literal here: streaming
        # used to hardcode its own wording, so the same failure read differently over
        # SSE than it did through `run_sync`, and only the sync copy told the operator
        # what to do next.
        if claims_action_without_evidence(
            called_tools, successful_tools, policy.mutation_tool_names(),
        ):
            logger.warning(
                "[%s] action_guard tripped — completion claim without a "
                "successful mutation tool. successful=%s",
                log_prefix, sorted(successful_tools),
            )
            yield ErrorEvent(error=policy.no_evidence_reply())

    if run_cost is not None:
        yield DoneEvent(
            total_tokens=total_tokens,
            tokens_input=run_cost.tokens_input,
            tokens_output=run_cost.tokens_output,
            cost_usd=run_cost.cost_usd,
        )
    else:
        yield DoneEvent(total_tokens=total_tokens)
