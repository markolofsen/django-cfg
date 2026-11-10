"""Keep one answer's tool traffic bounded: a soft tool cap and two compaction tiers, as agent hooks.

* `soft_cap(n)` is a `prepare_tools` hook: after `n` tool calls in the run every tool is hidden, so the model answers in
  words. (`KindLimits.tool_calls_limit` is the hard cap: it ends the run in `error`.)
* `compactor(keep, clamp)` is a history processor run before each model request: tier 1 cuts a tool result longer than `clamp`
  characters (and says how much was kept: `[cut: kept N of M chars]`), tier 2 replaces every tool result but the newest `keep` with a stub. Only what the model reads changes; the
  stored `tool_calls` are untouched.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace
from typing import Any

from pydantic_ai.messages import ModelMessage, ModelRequest, ToolReturnPart

from django_cfg.modules.django_llm.agent.runtime.clamp import clamp_text

STUB = "[earlier tool result left out]"


def soft_cap(limit: int) -> Callable[[Any, list], list]:
    def prepare(ctx: Any, tool_defs: list) -> list:
        return [] if ctx.usage.tool_calls >= limit else tool_defs

    return prepare


def compactor(keep: int | None, clamp: int | None) -> Callable[[list[ModelMessage]], list[ModelMessage]]:
    def process(messages: list[ModelMessage]) -> list[ModelMessage]:
        positions = [(i, j) for i, m in enumerate(messages) if isinstance(m, ModelRequest) for j, p in enumerate(m.parts) if isinstance(p, ToolReturnPart)]
        old = set(positions[: max(0, len(positions) - keep)]) if keep is not None else set()
        if not old and clamp is None:
            return messages
        out = list(messages)
        for i, j in positions:
            part = out[i].parts[j]
            content = STUB if (i, j) in old else part.content
            if clamp is not None and isinstance(content, str):
                content = clamp_text(content, clamp)
            if content is not part.content:
                parts = list(out[i].parts)
                parts[j] = replace(part, content=content)
                out[i] = replace(out[i], parts=parts)
        return out

    return process
