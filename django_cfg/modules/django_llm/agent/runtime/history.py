"""Conversation history conversion: dict → pydantic-ai ModelMessage list.

The agent's memory of its own actions lives here.

Until 2026-07 this module dropped every tool call on the floor: it mapped
``user`` and ``assistant`` text and nothing else. The calls were persisted
(``ChatMessage.tool_calls``, a JSONField the views layer fills from the SSE
stream) and then never replayed — so on turn N the model could not see that
it had already looked a client up on turn N-1, and it looked them up again.
The ``per_turn_call_cap`` capability exists to cut that loop off. Replaying
the calls removes the reason for the loop.
"""

from __future__ import annotations

import json
from typing import Any

from pydantic_ai.messages import (
    ModelMessage,
    ModelRequest,
    ModelResponse,
    TextPart,
    ToolCallPart,
    ToolReturnPart,
    UserPromptPart,
)


def _tool_parts(tool_calls: list[dict]) -> tuple[list[ToolCallPart], list[ToolReturnPart]]:
    """Rebuild the call/return pair for each persisted tool call.

    A provider rejects a ``ToolCallPart`` with no matching ``ToolReturnPart``,
    so a call whose result never landed (the run died mid-tool, the browser
    disconnected) is dropped entirely rather than replayed half-formed.
    """
    calls: list[ToolCallPart] = []
    returns: list[ToolReturnPart] = []

    for entry in tool_calls:
        if not isinstance(entry, dict):
            continue
        name = entry.get("name") or ""
        call_id = str(entry.get("id") or "")
        if not name or not call_id:
            continue
        # ``output`` is None while the call is still running. A pair that
        # never completed cannot be replayed — see the docstring.
        output = entry.get("output")
        if output is None:
            continue

        args: Any = entry.get("input")
        if not isinstance(args, (dict, str)):
            args = {} if args is None else json.dumps(args)

        calls.append(ToolCallPart(tool_name=name, args=args, tool_call_id=call_id))
        returns.append(
            ToolReturnPart(
                tool_name=name,
                content=output,
                tool_call_id=call_id,
            )
        )

    return calls, returns


def convert_history(history: list[dict]) -> list[ModelMessage]:
    """Convert ``[{"role", "content", "tool_calls"?}]`` to ``ModelMessage``s.

    An assistant turn that used tools becomes the pair of messages the model
    actually produced: a ``ModelResponse`` carrying its ``ToolCallPart``s (and
    its text, if any), followed by a ``ModelRequest`` carrying the matching
    ``ToolReturnPart``s. That is the shape pydantic-ai itself writes, so the
    replayed history is indistinguishable from a live run.

    Roles other than ``user`` / ``assistant`` are dropped — the views layer
    persists only those two.
    """
    messages: list[ModelMessage] = []

    for item in history:
        role = item.get("role", "")
        content = item.get("content", "")

        if role == "user":
            messages.append(ModelRequest(parts=[UserPromptPart(content=content)]))
            continue

        if role != "assistant":
            continue

        raw_calls = item.get("tool_calls") or []
        calls, returns = _tool_parts(raw_calls) if isinstance(raw_calls, list) else ([], [])

        if not calls:
            messages.append(ModelResponse(parts=[TextPart(content=content)]))
            continue

        # The model called tools on this turn. Replay the call, then the
        # result, then whatever it said afterwards — in that order, or the
        # text would appear to precede the evidence it was based on.
        messages.append(ModelResponse(parts=list(calls)))
        messages.append(ModelRequest(parts=list(returns)))
        if content:
            messages.append(ModelResponse(parts=[TextPart(content=content)]))

    return messages
