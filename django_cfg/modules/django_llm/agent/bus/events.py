"""SSE event types for chat streaming."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class TextDeltaEvent:
    delta: str = ""
    type: str = field(default="text_delta", init=False)

    def to_sse(self) -> str:
        return f"data: {json.dumps({'type': self.type, 'delta': self.delta})}\n\n"


@dataclass
class ToolCallEvent:
    tool: str
    args: Any
    type: str = field(default="tool_call", init=False)

    def to_sse(self) -> str:
        return f"data: {json.dumps({'type': self.type, 'tool': self.tool, 'args': self.args})}\n\n"


@dataclass
class ToolResultEvent:
    tool: str
    result: Any
    data: Any = None  # structured JSON for the frontend; result is the LLM-facing text
    type: str = field(default="tool_result", init=False)

    def to_sse(self) -> str:
        payload: dict[str, Any] = {"type": self.type, "tool": self.tool, "result": self.result}
        if self.data is not None:
            payload["data"] = self.data
        return f"data: {json.dumps(payload)}\n\n"


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
    type: str = field(default="done", init=False)

    def to_sse(self) -> str:
        return f"data: {json.dumps({
            'type': self.type,
            'total_tokens': self.total_tokens,
            'tokens_input': self.tokens_input,
            'tokens_output': self.tokens_output,
            'cost_usd': self.cost_usd,
        })}\n\n"


@dataclass
class ErrorEvent:
    error: str
    type: str = field(default="error", init=False)

    def to_sse(self) -> str:
        return f"data: {json.dumps({'type': self.type, 'error': self.error})}\n\n"


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
    data: dict
    type: str = field(default="ui_payload", init=False)

    def to_sse(self) -> str:
        payload = {"type": self.type, "kind": self.kind, "data": self.data}
        return f"data: {json.dumps(payload)}\n\n"


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


SSEEvent = (
    TextDeltaEvent
    | ToolCallEvent
    | ToolResultEvent
    | UIPayloadEvent
    | DirectiveEvent
    | DoneEvent
    | ErrorEvent
    | ApprovalRequiredEvent
)
