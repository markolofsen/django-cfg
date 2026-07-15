"""Intent-router capability — a deliberate no-op, kept for the hook contract.

It once pruned a ~30-tool admin surface down to 5–10 based on a bilingual phrase
corpus (Russian + English keywords → tool buckets). The corpus was brittle: every
new colloquialism missed its bucket, every locale added maintenance, and modern
frontier models route over the full surface without drowning. So the routing is gone
and the capability now passes tools through untouched.

It survives only so a host's capability list does not have to change shape, and so
the ordering of the surrounding hooks stays stable. **If nothing depends on that,
delete it** — a no-op that nobody needs is worse than no file.

The CRM tool names that used to live here have moved back to CRM
(`chat/agent/runtime/action_guard_policy.py`). They were host policy sitting in a
reusable module: `send_customer_message` means nothing to any other host.
"""

from __future__ import annotations

from typing import Any

from pydantic_ai import RunContext
from pydantic_ai.capabilities import Hooks


def intent_router_capability(history: list[dict]) -> Hooks[Any]:
    """No-op pass-through hooks (see module docstring)."""

    def _prepare(ctx: RunContext[Any], tool_defs: list[Any], /) -> list[Any]:
        return tool_defs

    return Hooks(prepare_tools=_prepare)
