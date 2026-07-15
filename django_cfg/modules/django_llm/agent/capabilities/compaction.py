"""Context compaction — keep the conversation inside a token budget.

Before this existed the agent bounded its history by counting rows: 20
messages for chat, 50 for the autonomous reply. Nothing measured tokens, so
a handful of long tool results could push a "20-message" history past
30k tokens, and nothing summarized the tail — it was simply carried, in
full, on every single turn, forever.

The strategy is tiered, cheapest first, and only escalates when the cheap
tiers have not brought the history back under budget:

1. ``ClampOversizedMessages`` — truncate any single oversized part. One
   ``query_table`` result should not be able to dominate the window.
2. ``ClearToolResults`` — blank the *content* of old tool results while
   keeping the call/return pair intact. The model still sees THAT it
   looked something up, which is what stops it looking it up again; it
   just no longer re-reads the 4 000-token answer from ten turns ago.
3. ``SummarizingCompaction`` — an LLM pass that replaces the old tail with
   a structured summary. The expensive one, so it runs last.

The pairing invariant is upstream's, not ours: a ``ToolCallPart`` is never
separated from its ``ToolReturnPart``, because a provider rejects an orphan.
"""

from __future__ import annotations

import warnings
from typing import Any

# Upstream graduated these out of ``experimental`` on 2026-07-10, one day after
# the 0.6.0 release we pin — so the flat ``pydantic_ai_harness.compaction`` path
# is not on PyPI yet. Move these imports when we take 0.7.
#
# The experimental warning is silenced deliberately, and only here: importing
# this module IS the decision to accept the API risk, and re-emitting the
# warning on every worker boot would train everyone to ignore the log.
from pydantic_ai_harness.experimental import HarnessExperimentalWarning

with warnings.catch_warnings():
    warnings.simplefilter("ignore", HarnessExperimentalWarning)
    from pydantic_ai_harness.experimental.compaction import (
        ClampOversizedMessages,
        ClearToolResults,
        SummarizingCompaction,
        TieredCompaction,
    )


def build_compaction_capability(
    *,
    max_tokens: int,
    keep_tokens: int,
    summary_model: Any,
) -> TieredCompaction:
    """Assemble the compaction tier stack for a chat agent.

    ``summary_model`` is a resolved pydantic-ai model — passing the slug
    would make the summarizer bypass the project's fallback chain, so an
    outage on the summarizer's provider would take the whole turn down
    rather than degrading.
    """
    return TieredCompaction(
        tiers=[
            # A single tool result should never be able to eat the budget.
            # 6k tokens is generous for a CRM read and ruinous for a
            # `peek_table` dump. This one is unconditional — an oversized
            # part is worth clamping whatever the total looks like.
            ClampOversizedMessages(max_part_tokens=6_000),
            # Keep the last few call/return pairs readable; blank the rest.
            # The call itself survives — that is the agent's memory of what
            # it already did, and the reason it stops re-calling.
            #
            # Each tier carries its own trigger: ``TieredCompaction`` runs
            # them in order until the history is back under target, it does
            # not push its own budget down into them.
            ClearToolResults(max_tokens=max_tokens, keep_pairs=4),
            # Last resort: an LLM pass that summarizes the tail.
            SummarizingCompaction(
                model=summary_model,
                max_tokens=max_tokens,
                keep_tokens=keep_tokens,
            ),
        ],
        target_tokens=max_tokens,
    )
