"""Layer 3 — post-run anti-hallucination gate.

The structural backstop against the "intent-as-completion" failure mode:
a cheap model that says "Message sent" / "task created" without ever
firing (or successfully completing) the matching mutation tool.

Prior versions tried to detect a completion claim by regex-matching
past-tense verb stems in the assistant's text (bilingual EN + RU).
That heuristic was brittle and language-bound, so this version drops
NLP entirely and uses a purely structural rule: if any mutation tool
was attempted this turn and none of them returned a successful result,
the gate trips — regardless of what the assistant wrote. Read-only
turns and turns with at least one successful mutation pass through.

- Layer 1 (mutation tools always in surface) — ``intent_router.py``.
- Layer 2 (evidence-attribution rule in the system prompt) — the host's prompt.
- Layer 3 (this file) — runs AFTER the model is done. It cannot be
  bypassed by the model, so it is the absolute backstop.

**The algorithm is generic; the evidence is not.** *Which* tools count as mutations
is host policy — a CRM's ``send_customer_message`` means nothing to another host —
and so is the text to show when the guard trips. Both used to be hardcoded here, and
that is precisely what kept this file trapped inside CRM. They are now arguments.

The host does not have to hand-maintain a parallel list: a ``ToolProvider`` already
classifies every tool by ``ToolMeta.category``, so the mutation set is just
``{name for name, cat in categories.items() if cat == "mutation"}``. A second
hand-written list is a second thing to forget to update — which is exactly the bug
this guard exists to catch, one level up.
"""

from __future__ import annotations

import json


def tool_return_succeeded(content: object) -> bool:
    """True if a tool's return content represents a SUCCESS (not a ToolError).

    A ``BaseTool`` serializes a ToolError as ``{"error": ...}`` and a success as its
    ``result_schema`` dump (no ``error`` key). This reads the harness's own wire
    format — nothing host-specific — so it lives here, next to its only caller.

    **Conservative by design.** Only returns True when a payload can be positively
    parsed AND lacks an error marker. Unparseable content → False, i.e. "no
    evidence". That is the safe side of an asymmetric gate: a mis-read success
    produces a spurious warning, while a mis-read failure lets a fabricated "sent"
    through — the exact thing the guard exists to stop.
    """
    from django_cfg.modules.django_llm.agent.tools.core._base_tool import strip_raw

    payload: dict = {}
    if isinstance(content, str):
        clean, embedded = strip_raw(content)
        if isinstance(embedded, dict):
            payload = embedded
        else:
            try:
                payload = json.loads(clean)
            except (json.JSONDecodeError, ValueError):
                return False
    elif isinstance(content, dict):
        payload = content
    else:
        return False

    if not isinstance(payload, dict):
        return False
    # ToolError dumps carry a truthy "error". Success results don't.
    if payload.get("error"):
        return False
    # An explicit ok=False (some result schemas carry it) is a failure too.
    if payload.get("ok") is False:
        return False
    return True


def claims_action_without_evidence(
    called_tools: list[str],
    successful_mutation_tools: set[str],
    mutation_tool_names: frozenset[str] | set[str],
) -> bool:
    """Decide whether this turn ran a mutation that didn't succeed.

    Args:
        called_tools: tool names the model invoked this turn (any kind).
        successful_mutation_tools: subset whose return parsed as a
            non-error result. A ToolError must NOT appear here — a
            failed ``confirm_send`` is not evidence of a send.
        mutation_tool_names: which tools count as mutations at all.
            HOST-SUPPLIED — the harness cannot know which of a host's tools
            change the world.

    Returns:
        True  → at least one mutation tool was attempted AND none
                of the attempts succeeded. Caller should replace the
                assistant text with its own "no evidence" notice.
        False → either no mutation was attempted, or at least one
                mutation succeeded.
    """
    attempted_mutations = {t for t in called_tools if t in mutation_tool_names}
    if not attempted_mutations:
        return False
    return not (attempted_mutations & successful_mutation_tools)
