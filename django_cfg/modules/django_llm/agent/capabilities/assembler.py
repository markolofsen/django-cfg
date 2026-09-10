"""Assemble a run's capability list — one place, one order.

pydantic-ai capabilities are order-sensitive hooks. Four call sites in CRM each
hand-rolled their own list, and they had drifted: the chat agent ran five, onboarding
ran one, e2e ran two, and the research agent ran **none** — so a cheap model's
stringified-JSON args (`"[\"Q1\"]"` instead of `["Q1"]`) bounced its way through
`retries` and the run failed, silently, on every research call. A hand-maintained list
per site is four things to keep in sync; they weren't.

This is the single assembler. A caller states WHICH capabilities it wants and their
parameters (a `CapabilitySpec`); the assembler owns the ORDER and the construction.
`lenient_json_args` is not a flag — it is always on, because every host talks to the
same cheap models and every host needs the same defence. The rest are opt-in.

The order is deliberate and is the assembler's responsibility, not the caller's:

    lenient_json_args → intent_router → per_turn_call_cap → compaction → code_mode

`lenient_json_args` first so later hooks see already-decoded args. `compaction` and
`code_mode` last because they are the heavy, situational ones.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


@dataclass(frozen=True, slots=True)
class CapabilitySpec:
    """Which capabilities a run wants, and the parameters they need.

    `lenient_json_args` is intentionally absent — it is unconditional. Everything
    here is opt-in; the default spec is "lenient only", which is the safe minimum
    (and what a bare agent like the research agent should have had all along).
    """

    #: Prune the tool surface to a per-turn subset from the user message. Needs the
    #: history to reason about the current turn. None → not installed.
    intent_router_history: Optional[list[dict]] = None

    #: Drop a tool from the surface once it has been over-called this turn (the
    #: empty-args re-call backstop). A plain flag — the cap reads its counters off
    #: deps at run time.
    per_turn_call_cap: bool = False

    #: Token-bounded history compaction. The host builds the summary model (only it
    #: knows its model policy) and passes the ready capability object through. None →
    #: not installed. Typed as Any to avoid importing pydantic-ai types here.
    compaction: Any = None

    #: Sandbox the named read tools into a single `run_code` (Monty). Empty/None →
    #: not installed. The host decides which reads are safe to sandbox.
    sandboxed_tools: Optional[frozenset[str]] = None

    #: The host's WRITE tool names — surfaced only as examples in code_mode's
    #: "the write tools don't exist in the sandbox" note, so the harness prompt cites
    #: the host's real tools instead of hardcoding CRM's. Ignored unless
    #: `sandboxed_tools` installs code_mode. None → the note stands without examples.
    sandbox_write_tools: Optional[frozenset[str]] = None


def build_capabilities(spec: CapabilitySpec) -> list[Any]:
    """Return the ordered capability list for a run.

    `lenient_json_args` is always first and always present. The rest are appended in
    the fixed order above when the spec asks for them.
    """
    from modules.django_llm.agent.capabilities import (
        intent_router_capability,
        lenient_json_args_capability,
        per_turn_call_cap_capability,
    )

    caps: list[Any] = [lenient_json_args_capability()]

    if spec.intent_router_history is not None:
        caps.append(intent_router_capability(spec.intent_router_history))

    if spec.per_turn_call_cap:
        caps.append(per_turn_call_cap_capability())

    if spec.compaction is not None:
        caps.append(spec.compaction)

    if spec.sandboxed_tools:
        from modules.django_llm.agent.capabilities.code_mode import (
            build_code_mode_capability,
        )

        caps.append(build_code_mode_capability(
            tool_names=sorted(spec.sandboxed_tools),
            write_tool_names=(
                sorted(spec.sandbox_write_tools) if spec.sandbox_write_tools else None
            ),
        ))

    return caps
