"""Per-tool metadata: policy tags attached to ``@llm_tool`` callables.

This is our equivalent of pydantic-ai's ``ToolDefinition.metadata`` —
arbitrary tags that the LLM never sees, but the prompt/rubric layer
uses to compose only the policy text that's relevant to the actually
loaded tool set.

Pattern (mirrors pydantic-ai upstream):
    @llm_tool(result_schema=..., meta=ToolMeta(category="outbound_propose", ...))
    def propose_send_customer_message(...): ...

    # later, in the rubric composer:
    meta = get_tool_meta(propose_send_customer_message)  # ToolMeta | None

The decorator stores the meta on the wrapper as ``__llm_tool_meta__``
(dunder so tooling doesn't surface it as user-meaningful state).
"""

from __future__ import annotations

from typing import Any, Callable, Literal, Optional

from pydantic import BaseModel


ToolCategory = Literal[
    "read",                     # safe, no side effects
    "mutation",                 # writes local CRM state, not customer-visible
    "outbound_propose",         # stages a customer-visible send
    "outbound_confirm",         # commits a staged send
    "outbound_cancel",          # cancels a staged send
    "outbound_query",           # segmentation read used to feed a propose
    "kb_read",                  # knowledge-base search / retrieval
    "profile",                  # current-user identity
    "url_builder",              # pure URL resolution, no DB side-effects
    "conversation",             # customer-visible conversation action (interim messages, typing)
]


_DEFAULT_TIMEOUTS_BY_CATEGORY: dict[str, float] = {
    "read": 5.0,
    "kb_read": 15.0,
    "profile": 3.0,
    "outbound_query": 10.0,
    "outbound_propose": 15.0,
    "outbound_confirm": 30.0,
    "outbound_cancel": 5.0,
    "mutation": 10.0,
}


class ToolMeta(BaseModel):
    """Policy tags attached to a tool function.

    Fields are deliberately small and strongly typed — the rubric
    layer matches on them, so any new flag should justify itself
    against an actual rubric that needs it.
    """

    category: ToolCategory
    customer_visible: bool = False
    """True if invoking this tool can produce a side-effect a customer
    can directly observe (email sent, message posted to a channel,
    etc.). The propose/confirm rubric keys off this."""

    requires_confirm: bool = False
    """True if this tool produces a proposal that another tool must
    confirm in a later turn. Used by rubrics that warn the agent
    against auto-chaining propose → confirm."""

    portable: bool = True
    """False marks a tool tied to project-specific assumptions (custom
    DB schema, third-party SaaS) that shouldn't be lifted into other
    projects without rework. Currently informational only — no rubric
    keys off it yet."""

    timeout_seconds: float | None = None
    """Per-tool execution timeout. ``None`` falls back to the default
    for the tool's ``category`` (see ``_DEFAULT_TIMEOUTS_BY_CATEGORY``).
    A tool that exceeds its timeout returns a ``ToolError`` to the LLM
    instead of hanging the chat stream — the LLM then decides to retry
    a smaller call or surface the error to the admin."""

    requires_approval: bool = False
    """True if this tool must run through pydantic-ai's deferred-tool
    HITL flow. The agent runner registers it via
    ``Tool(fn, requires_approval=True)``: when the model calls it, the
    run cleanly ends with ``DeferredToolRequests`` instead of executing
    the body. The approval endpoint resumes with
    ``deferred_tool_results`` once the admin clicks approve / deny / edit."""

    def resolved_timeout(self) -> float:
        if self.timeout_seconds is not None:
            return float(self.timeout_seconds)
        return _DEFAULT_TIMEOUTS_BY_CATEGORY.get(self.category, 10.0)


_META_ATTR = "__llm_tool_meta__"
_SANDBOX_ATTR = "__llm_tool_sandbox__"


def attach_meta(fn: Callable[..., Any], meta: ToolMeta) -> None:
    """Stamp ``meta`` onto ``fn`` so ``get_tool_meta`` can recover it.

    Called by the ``@llm_tool`` decorator. Not for end-user code.
    """
    setattr(fn, _META_ATTR, meta)


def get_tool_meta(fn: Callable[..., Any]) -> Optional[ToolMeta]:
    """Return the ``ToolMeta`` attached by ``@llm_tool``, or ``None``."""
    return getattr(fn, _META_ATTR, None)


def attach_sandbox_callable(fn: Callable[..., Any], sandbox_fn: Callable[..., Any]) -> None:
    """Stamp a tool's ``CodeMode`` projection onto its native callable.

    Tool modules export a *callable*, not the ``BaseTool`` instance
    (``list_tasks = ListTasksTool().as_callable()``), so by the time the registry
    hands tools to the agent the instance is gone and
    ``as_sandbox_callable()`` is out of reach.

    Rather than add a second registry that could drift from the first, the native
    callable carries its own sandbox twin — same mechanism as ``attach_meta``. One
    ``BaseTool`` remains the single source of both projections.
    """
    setattr(fn, _SANDBOX_ATTR, sandbox_fn)


def get_sandbox_callable(fn: Callable[..., Any]) -> Optional[Callable[..., Any]]:
    """Return the ``CodeMode`` projection of ``fn``, or ``None``.

    ``None`` means the tool is not sandboxable — a plain ``@llm_tool`` callable
    with no ``BaseTool`` behind it, which returns prose and would be unusable
    inside ``run_code``. Callers keep such tools on the native path.
    """
    return getattr(fn, _SANDBOX_ATTR, None)
