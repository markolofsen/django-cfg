"""Synchronous agent run — the sync twin of ``streaming.py``.

``streaming.py`` drives a pydantic-ai ``Agent`` and yields SSE events; this drives
the same ``Agent`` once and returns a single structured result. Both share the same
per-run machinery — the ``UsageLimits`` cap, the message scan that counts turns and
collects ``called_tools`` / ``successful_tools``, ``price_run``, and the Layer-3
action guard reached through ``deps.action_guard_policy``. Neither imports a host.

Why a function and not more of ``ChatAgent``: the loop had drifted from streaming's.
It reached the action guard by importing CRM directly (``mutation_tool_names`` /
``NO_EVIDENCE_REPLY``) instead of through the ``ActionGuardPolicy`` seam the stream
path already used — so the harness's own sync path was the one place that broke the
"no host imports" rule the rest of the plane now enforces. Pulling it here fixes that
by construction: this file lives in ``agent/`` and cannot import CRM.

``extract_confirmation_token`` moves with it — it reads only the ``BaseTool`` wire
format (a ``_RAW_SENTINEL``-embedded payload), which is harness-generic. A host that
stages an outbound proposal reads the token off ``AgentSyncResult.pending_token``.
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from typing import Any

from pydantic_ai import Agent
from pydantic_ai.messages import ToolReturnPart

from modules.django_llm.agent.bus.result import AgentSyncResult
from modules.django_llm.agent.runtime.action_guard import (
    claims_action_without_evidence,
    tool_return_succeeded,
)
from modules.django_llm.agent.runtime.cost import price_run
from modules.django_llm.agent.tools.core._base_tool import strip_raw

logger = logging.getLogger(__name__)

#: Hard cap on model round-trips per run — the same limit streaming applies. Without
#: it, certain inputs (unicode control chars, overlong messages) make the model cycle
#: indefinitely; pydantic-ai has no built-in ceiling.
_REQUEST_LIMIT = 15
#: Wall-clock ceiling for one synchronous run. The streaming path has no equivalent
#: (the browser owns the timeout by disconnecting); a sync caller — a Telegram webhook
#: — needs its own, or a stuck run holds the worker forever.
_RUN_TIMEOUT_S = 90.0


def extract_confirmation_token(content: object) -> str | None:
    """Extract a ``ct_<hex>`` proposal token from a tool's return content.

    A ``propose_*`` tool stages an outbound send and returns a ``confirmation_token``
    in its payload; the caller (e.g. the Telegram dispatcher) reads it to attach an
    inline approval button. A successful ``BaseTool`` return is a string carrying a
    ``_RAW_SENTINEL``-embedded JSON payload *after* the LLM-facing text, so a bare
    ``json.loads`` on the whole string fails with "Extra data" and the token is lost —
    split the sentinel off with ``strip_raw`` first (its second element is the parsed
    dict). Falls back to parsing the cleaned text for tools with no embedded payload.

    Returns the token, or ``None`` when the tool staged no proposal.
    """
    payload: dict = {}
    if isinstance(content, str):
        clean, embedded = strip_raw(content)
        if isinstance(embedded, dict):
            payload = embedded
        else:
            try:
                payload = json.loads(clean)
            except (json.JSONDecodeError, ValueError):
                payload = {}
    elif isinstance(content, dict):
        payload = content
    token = payload.get("confirmation_token", "")
    if isinstance(token, str) and token.startswith("ct_"):
        return token
    return None


async def run_agent_sync(
    *,
    agent: Agent,
    deps: Any,
    user_message: str,
    message_history: list,
    is_admin_chat: bool,
    log_prefix: str = "Agent",
) -> AgentSyncResult:
    """Run a pydantic-ai ``Agent`` once and return a structured result.

    Owns the whole synchronous run: the ``UsageLimits`` cap, the ``wait_for``
    timeout, the message scan (turn counting, ``called_tools`` /
    ``successful_tools``, the pending proposal token), pricing, and the Layer-3
    action guard.

    The guard is reached through ``deps.action_guard_policy`` — the same seam
    streaming uses — so this loop, like streaming's, never imports a host. When the
    policy is absent (a host with no mutation concept) the guard is skipped.

    Never raises for a run-level failure: a timeout or model error returns an
    ``AgentSyncResult`` with an honest message, because the caller (a webhook, a bot)
    has no better place to render a traceback than the chat itself.
    """
    logger.info("[%s.run_sync] user_msg=%r", log_prefix, user_message[:120])
    t0 = time.monotonic()

    try:
        try:
            from pydantic_ai import UsageLimits
            limits = UsageLimits(request_limit=_REQUEST_LIMIT)
        except Exception:
            limits = None

        run_kwargs: dict = {"deps": deps, "message_history": message_history}
        if limits is not None:
            run_kwargs["usage_limits"] = limits

        result = await asyncio.wait_for(
            agent.run(user_message, **run_kwargs),
            timeout=_RUN_TIMEOUT_S,
        )
        elapsed = round((time.monotonic() - t0) * 1000)
        search_ctx = getattr(deps, "search_ctx", None)
        searches_used = len(search_ctx.searches) if search_ctx else 0

        pending_token, called_tools, successful_tools, model_turns = _scan_messages(
            result, len(message_history), log_prefix,
        )

        # Layer 3 gate: if the model claimed a completed action but no mutation tool
        # succeeded, replace the fabricated success with the policy's correction. The
        # guard is the harness's; the evidence and the copy are the host's — reached
        # through the ActionGuardPolicy seam, NOT imported. This is the fix that
        # brings the sync path back in line with streaming (which never imported CRM).
        output_text = result.output or ""
        policy = getattr(deps, "action_guard_policy", None)
        if is_admin_chat and policy is not None:
            if claims_action_without_evidence(
                called_tools, successful_tools, policy.mutation_tool_names(),
            ):
                logger.warning(
                    "[%s.run_sync] action_guard tripped — claim without a "
                    "successful mutation. called=%s successful=%s",
                    log_prefix, called_tools, sorted(successful_tools),
                )
                output_text = policy.no_evidence_reply()

        # Price the turn — never raises; cost is telemetry, not the answer.
        run_cost = price_run(
            getattr(result, "usage", None),
            str(getattr(getattr(result, "response", None), "model_name", "") or ""),
        )

        logger.info(
            "[%s.run_sync] done  output_len=%d  model_turns=%d  tool_calls=%d  "
            "elapsed_ms=%d  searches=%d  tokens=%d/%d  cost_usd=%s",
            log_prefix, len(result.output or ""), model_turns, len(called_tools),
            elapsed, searches_used,
            run_cost.tokens_input, run_cost.tokens_output, run_cost.cost_usd,
        )
        return AgentSyncResult(
            text=output_text,
            pending_token=pending_token,
            called_tools=called_tools,
            cost=run_cost,
        )
    except asyncio.CancelledError:
        raise
    except asyncio.TimeoutError:
        logger.error("[%s.run_sync] timed out after %.0fs", log_prefix, _RUN_TIMEOUT_S)
        return AgentSyncResult(
            text="Request timed out. Please try again.",
            pending_token=None,
        )
    except Exception as exc:
        logger.exception("[%s.run_sync] error: %s", log_prefix, exc)
        return AgentSyncResult(text=f"Error: {exc}", pending_token=None)


def _scan_messages(
    result: Any, history_len: int, log_prefix: str,
) -> tuple[str | None, list[str], set[str], int]:
    """Walk a completed run's messages: the per-turn trace + Layer-3 evidence.

    Returns ``(pending_token, called_tools, successful_tools, model_turns)``:

    - ``pending_token``  — a ``ct_<hex>`` proposal token if a tool staged a send.
    - ``called_tools``   — every tool the run touched, in first-seen order. A
      ``ToolCallPart`` (intent) or ``ToolReturnPart`` (proof it ran) both count as
      "attempted" for the guard's structural rule.
    - ``successful_tools`` — the subset whose RETURN parsed as a success (not a
      ToolError). This is what separates a real mutation from a fabricated "sent".
    - ``model_turns``    — NEW ``ModelResponse`` turns only (``history_len`` skips the
      replayed prior history), for the operator-facing reasoning trace.

    Best-effort: a scan failure logs and returns what it has, because the run already
    produced an answer — the trace is telemetry, not the result.
    """
    pending_token: str | None = None
    called_tools: list[str] = []
    successful_tools: set[str] = set()
    model_turns = 0

    try:
        all_msgs = result.all_messages()
        for idx, msg in enumerate(all_msgs):
            if type(msg).__name__ == "ModelResponse" and idx >= history_len:
                model_turns += 1
                turn_tools: list[str] = []
                has_text = False
                for part in getattr(msg, "parts", ()):
                    part_type = type(part).__name__
                    if part_type == "TextPart":
                        has_text = True
                    elif hasattr(part, "tool_name"):
                        turn_tools.append(part.tool_name)
                logger.info(
                    "[%s.run_sync] model_turn=%d  tool_calls=%s  has_text=%s",
                    log_prefix, model_turns, turn_tools, has_text,
                )
        for msg in all_msgs:
            for part in getattr(msg, "parts", ()):
                tool_name = getattr(part, "tool_name", None)
                if not tool_name:
                    continue
                if tool_name not in called_tools:
                    called_tools.append(tool_name)
                if isinstance(part, ToolReturnPart):
                    token = extract_confirmation_token(part.content)
                    if token:
                        pending_token = token
                    if tool_return_succeeded(part.content):
                        successful_tools.add(tool_name)
    except Exception:
        logger.debug("[%s.run_sync] message scan failed", log_prefix, exc_info=True)

    return pending_token, called_tools, successful_tools, model_turns
