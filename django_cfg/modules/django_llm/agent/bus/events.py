"""SSE event types for chat streaming.

Two dialects, one set of event objects
--------------------------------------

* ``admin`` (the default, unchanged): what the admin chat and ``django_mcp`` read.
  ``event.to_sse()`` and ``encode_sse(event)`` produce it: ``done`` carries
  ``total_tokens`` / ``tokens_input`` / ``tokens_output``, ``error`` carries one
  ``error`` string, ``tool_call`` / ``tool_result`` / ``directive`` /
  ``approval_required`` are frames.
* ``widget``: the wire ``@djangocfg/widget-chat/assistant`` decodes (its
  ``src/assistant/wire/frames.ts``; the page is the widget's ``@docs/wire-contract.md``).
  ``event.to_wire()`` and ``encode_sse(event, wire="widget")`` produce it: ``run``
  (first, versioned), ``status`` (``thinking`` / ``searching`` / ``answering``),
  ``text_delta``, optional ``reasoning_delta`` / ``reasoning_end`` / ``trace_step``, ``ui_payload``, ``done`` with ``tokens_in`` / ``tokens_out`` /
  ``cost_usd`` / ``finish_reason`` and ``error`` with ``code`` / ``message`` /
  ``retryable``. Events with no widget frame (``tool_call``, ``tool_result``,
  ``directive``, ``approval_required``) encode to ``None``: **a public chat must
  never forward tool names, arguments or results**, so the widget dialect has no
  frame for them.

The widget dialect is pinned by ``tests/fixtures/events.json`` (a copy of the
widget's own fixture; ``test_wire_contract.py`` fails on drift in either direction).
A changed field is a ``WIRE_VERSION`` bump; a new frame type is forward compatible
(old decoders ignore it).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Mapping, Optional

#: Version carried by the ``run`` frame. Bump it when a frame's field changes.
WIRE_VERSION = 1

#: Values of ``status.phase`` the widget understands.
WIRE_PHASES = ("thinking", "searching", "answering")

#: Values of ``error.code`` the widget understands. Anything else is sent as ``failed``.
WIRE_ERROR_CODES = ("unavailable", "timeout", "failed")

#: Response headers an SSE route must send (proxies and Cloudflare must not buffer or cache it).
SSE_HEADERS = {"Cache-Control": "no-cache, no-transform", "X-Accel-Buffering": "no"}

#: An SSE comment, ignored by clients; keeps proxies from closing an idle stream.
PING = ": ping\n\n"


@dataclass
class TextDeltaEvent:
    delta: str = ""
    type: str = field(default="text_delta", init=False)

    def to_sse(self) -> str:
        return f"data: {json.dumps({'type': self.type, 'delta': self.delta})}\n\n"

    def to_wire(self) -> dict[str, Any]:
        return {"type": self.type, "delta": self.delta}


@dataclass
class ToolCallEvent:
    tool: str
    args: Any
    # Not on any wire: lets a host pair a call with its result (replay needs the id).
    tool_call_id: str = ""
    type: str = field(default="tool_call", init=False)

    def to_sse(self) -> str:
        return f"data: {json.dumps({'type': self.type, 'tool': self.tool, 'args': self.args})}\n\n"

    def to_wire(self) -> None:
        return None  # a public chat must not see the tool surface


@dataclass
class ToolResultEvent:
    tool: str
    result: Any
    data: Any = None  # structured JSON for the frontend; result is the LLM-facing text
    tool_call_id: str = ""  # not on any wire
    type: str = field(default="tool_result", init=False)

    def to_sse(self) -> str:
        payload: dict[str, Any] = {"type": self.type, "tool": self.tool, "result": self.result}
        if self.data is not None:
            payload["data"] = self.data
        return f"data: {json.dumps(payload)}\n\n"

    def to_wire(self) -> None:
        return None  # a public chat must not see the tool surface


@dataclass
class DoneEvent:
    total_tokens: Optional[int] = None
    # The input/output split and the priced cost of the run. `cost_usd` is None when
    # the run could not be priced (no key, unknown model) — distinct from 0.0, a real
    # free-tier price. All three default to None so a run that never reported usage
    # (e.g. a deferred/HITL turn) serializes exactly as before.
    tokens_input: Optional[int] = None
    tokens_output: Optional[int] = None
    cost_usd: Optional[float] = None
    # Widget dialect only (not in the admin frame): why the run ended and whether the
    # stored answer was replayed instead of run.
    finish_reason: Optional[str] = None
    replayed: bool = False
    # Not on either wire: the slug that served the run (for the host's storage).
    model: Optional[str] = None
    type: str = field(default="done", init=False)

    def to_sse(self) -> str:
        return f"data: {json.dumps({
            'type': self.type,
            'total_tokens': self.total_tokens,
            'tokens_input': self.tokens_input,
            'tokens_output': self.tokens_output,
            'cost_usd': self.cost_usd,
        })}\n\n"

    def to_wire(self) -> dict[str, Any]:
        body: dict[str, Any] = {
            "type": self.type,
            "finish_reason": self.finish_reason or "stop",
            "tokens_in": self.tokens_input,
            "tokens_out": self.tokens_output,
            "cost_usd": self.cost_usd,
        }
        if self.replayed:  # the wire carries the flag only when true
            body["replayed"] = True
        return body


@dataclass
class ErrorEvent:
    error: str
    # Widget dialect only (the admin frame stays ``{type, error}``): a machine code the
    # client maps to its own sentence, and whether a resend can help.
    code: Optional[str] = None
    retryable: bool = True
    type: str = field(default="error", init=False)

    def to_sse(self) -> str:
        return f"data: {json.dumps({'type': self.type, 'error': self.error})}\n\n"

    def to_wire(self) -> dict[str, Any]:
        code = self.code if self.code in WIRE_ERROR_CODES else "failed"
        return {"type": self.type, "code": code, "message": self.error, "retryable": self.retryable}


@dataclass
class UIPayloadEvent:
    """Structured UI hint emitted alongside (not as part of) the tool flow.

    Carries typed product-widget data (vehicle cards, tax breakdowns, etc.)
    that the frontend renders independently of ``tool_call`` / ``tool_result``
    debug frames. Always safe to ship to public chat clients — by design
    it contains only what the widget needs, not the raw tool surface.

    See ``apps/crm/apps/chat/agent/runtime/ui_payloads.py`` for the
    typed payload models.
    """

    kind: str
    data: Any  # any JSON value; the host that registered the kind knows its shape
    # Not on the wire body: the stream position (the SSE ``id:``) the driver stamps, stored with the part so a resume sends only the parts after it.
    event_seq: Optional[int] = None
    type: str = field(default="ui_payload", init=False)

    def to_sse(self) -> str:
        payload = {"type": self.type, "kind": self.kind, "data": self.data}
        return f"data: {json.dumps(payload)}\n\n"

    def to_wire(self) -> dict[str, Any]:
        return {"type": self.type, "kind": self.kind, "data": self.data}


@dataclass
class DirectiveEvent:
    """UI directives the assistant wants applied to the user's screen.

    Carries `point` directives — "highlight / focus this element" — keyed
    by the CST ref ids (`@e4`) the page snapshot assigned. The frontend
    resolves each ref to a live DOM node and draws a highlight overlay.

    Read-only: a directive never changes the user's data, it only points
    at the UI. Emitted once per turn, just before ``DoneEvent``.
    """

    directives: list[Any]
    type: str = field(default="directive", init=False)

    def to_sse(self) -> str:
        payload = {"type": self.type, "directives": self.directives}
        return f"data: {json.dumps(payload)}\n\n"

    def to_wire(self) -> None:
        return None  # no widget frame


@dataclass
class ApprovalRequiredEvent:
    """A tool call needs human approval before its body can execute.

    Emitted by ``ChatAgent.stream()`` when pydantic-ai's run ends with
    ``DeferredToolRequests``. The frontend renders a preview + Approve
    / Deny / Edit UI, then POSTs back to the approval endpoint, which
    resumes the same Agent.run with ``DeferredToolResults``.
    """

    tool_call_id: str
    tool: str
    args: Any
    session_id: str = ""
    type: str = field(default="approval_required", init=False)

    def to_sse(self) -> str:
        payload = {
            "type": self.type,
            "tool_call_id": self.tool_call_id,
            "tool": self.tool,
            "args": self.args,
            "session_id": self.session_id,
        }
        return f"data: {json.dumps(payload)}\n\n"

    def to_wire(self) -> None:
        return None  # no widget frame: approvals are an admin-chat flow


@dataclass
class ReasoningDeltaEvent:
    """Widget dialect, optional: a piece of the model's thinking. Live view only, never stored.

    Emitted only when the host asks for it (``stream_agent_run(emit_reasoning=True)``): a public
    chat must not stream thinking it does not want a visitor to read.
    """

    delta: str = ""
    type: str = field(default="reasoning_delta", init=False)

    def to_sse(self) -> str:
        return encode_sse(self, "widget") or ""

    def to_wire(self) -> dict[str, Any]:
        return {"type": self.type, "delta": self.delta}


@dataclass
class ReasoningEndEvent:
    """Widget dialect, optional: seals the open thought with what the engine measured (``None`` = unknown)."""

    elapsed_ms: Optional[int] = None
    tokens: Optional[int] = None
    type: str = field(default="reasoning_end", init=False)

    def to_sse(self) -> str:
        return encode_sse(self, "widget") or ""

    def to_wire(self) -> dict[str, Any]:
        return {"type": self.type, "elapsed_ms": self.elapsed_ms, "tokens": self.tokens}


@dataclass
class TraceStepEvent:
    """Widget dialect, optional: one step of the answer's trace (``agent/trace``), sent when it starts (``status: running``)
    and again, with the same ``step_id``, when it settles: the client upserts by ``step_id``.

    ``step`` is the already-redacted TraceStep v1 dict. ``event_seq`` is the stream position the driver stamps (it is also the
    SSE ``id:`` of the frame); it is absent from a stored or replayed step.
    """

    step: dict[str, Any]
    event_seq: Optional[int] = None
    type: str = field(default="trace_step", init=False)

    def to_sse(self) -> str:
        return encode_sse(self, "widget") or ""

    def to_wire(self) -> dict[str, Any]:
        body: dict[str, Any] = {"type": self.type}
        if self.event_seq is not None:
            body["event_seq"] = self.event_seq
        body["step"] = self.step
        return body


@dataclass
class RunEvent:
    """Widget dialect: the first frame of a stream, naming the stored rows.

    ``thread_id`` and ``message_id`` are required by the client (without them the
    frame is dropped); ``client_id`` is the user message's client-made id (or None)
    and ``seq`` the assistant message's sequence number (or None). ``resume`` is true
    on a stream that attaches to an answer already being written (a second tab, a
    reconnect): what follows is a catch-up from storage, not the run itself.
    """

    thread_id: str
    message_id: str
    client_id: Optional[str] = None
    seq: Optional[int] = None
    version: int = WIRE_VERSION
    resume: bool = False
    type: str = field(default="run", init=False)

    def to_sse(self) -> str:
        return encode_sse(self, "widget") or ""

    def to_wire(self) -> dict[str, Any]:
        body: dict[str, Any] = {
            "type": self.type,
            "version": self.version,
            "thread_id": str(self.thread_id),
            "message_id": str(self.message_id),
            "client_id": None if self.client_id is None else str(self.client_id),
            "seq": self.seq,
        }
        if self.resume:  # the wire carries the flag only when true
            body["resume"] = True
        return body


@dataclass
class StatusEvent:
    """Widget dialect: an ephemeral label (``thinking`` / ``searching`` / ``answering``).

    May repeat, is never stored. A public chat maps tool calls to phases here instead
    of forwarding tool names.
    """

    phase: str
    type: str = field(default="status", init=False)

    def to_sse(self) -> str:
        return encode_sse(self, "widget") or ""

    def to_wire(self) -> dict[str, Any]:
        return {"type": self.type, "phase": self.phase if self.phase in WIRE_PHASES else "thinking"}


SSEEvent = (
    RunEvent
    | StatusEvent
    | TextDeltaEvent
    | ReasoningDeltaEvent
    | ReasoningEndEvent
    | ToolCallEvent
    | ToolResultEvent
    | UIPayloadEvent
    | DirectiveEvent
    | DoneEvent
    | ErrorEvent
    | ApprovalRequiredEvent
)


def encode_sse(event: Any, wire: str = "admin", seq: Optional[int] = None) -> Optional[str]:
    """One event as an SSE data block, in the chosen dialect.

    ``wire="admin"`` (default) is ``event.to_sse()``, byte for byte what this module
    always produced. ``wire="widget"`` is the widget dialect; ``None`` means the event
    has no frame there (tool and directive events) and must be dropped. ``seq`` (widget only) adds
    an SSE ``id: <seq>`` line before the data, the position a client resumes from.
    """
    if wire == "admin":
        return event.to_sse()
    if wire != "widget":
        raise ValueError(f"unknown wire dialect: {wire!r} (use 'admin' or 'widget')")
    body = event.to_wire()
    if body is None:
        return None
    prefix = f"id: {seq}\n" if seq is not None else ""
    return f"{prefix}data: {json.dumps(body, ensure_ascii=False, default=str)}\n\n"


def event_from_wire(raw: Mapping[str, Any]) -> Any:
    """The event for a decoded widget-dialect dict (tests, replay, clients).

    Raises ``KeyError`` for an unknown ``type`` and ``TypeError`` for a malformed frame.
    """
    kind = raw["type"]
    if kind == "run":
        return RunEvent(
            thread_id=raw["thread_id"],
            message_id=raw["message_id"],
            client_id=raw.get("client_id"),
            seq=raw.get("seq"),
            version=raw.get("version", WIRE_VERSION),
            resume=bool(raw.get("resume", False)),
        )
    if kind == "status":
        return StatusEvent(phase=raw["phase"])
    if kind == "text_delta":
        return TextDeltaEvent(delta=raw["delta"])
    if kind == "reasoning_delta":
        return ReasoningDeltaEvent(delta=raw["delta"])
    if kind == "reasoning_end":
        return ReasoningEndEvent(elapsed_ms=raw.get("elapsed_ms"), tokens=raw.get("tokens"))
    if kind == "ui_payload":
        return UIPayloadEvent(kind=raw["kind"], data=raw["data"])
    if kind == "trace_step":
        return TraceStepEvent(step=raw["step"], event_seq=raw.get("event_seq"))
    if kind == "done":
        return DoneEvent(
            tokens_input=raw.get("tokens_in"),
            tokens_output=raw.get("tokens_out"),
            cost_usd=raw.get("cost_usd"),
            finish_reason=raw.get("finish_reason"),
            replayed=bool(raw.get("replayed", False)),
        )
    if kind == "error":
        return ErrorEvent(
            error=raw.get("message", ""),
            code=raw["code"],
            retryable=bool(raw.get("retryable", True)),
        )
    raise KeyError(kind)
