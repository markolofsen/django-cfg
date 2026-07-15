"""The seams. A host wires into the agent plane through these — and only these.

The harness must not import its host. Everything it needs from one is an interface,
so the same machinery serves CRM, django-cfg, or anything else.

**There are three. If a fourth appears, the boundary is cut in the wrong place** —
stop and re-cut it rather than adding a fourth.

These are `typing.Protocol`s, i.e. structural: a host satisfies one by having the
right shape, not by inheriting. No registration, no base class, no import from the
harness into the host or back.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ToolProvider(Protocol):
    """Answers "which tools exist for THIS run?"

    Deliberately per-run rather than a module-level table. Which tools exist depends
    on who is asking (an admin sees more than a customer), on the channel, and on the
    tier — so the answer is a function of `deps`, not a constant.

    That is also why it cannot be defaulted away: a stubbed provider returning an
    empty list would let the harness classify every tool as a read and silently stop
    capping mutations. An empty tool list is a real answer ("this principal has no
    tools"), never a fallback for "we could not find out".
    """

    def get_tools(self) -> list[Any]:
        """Every tool callable available to this run, flat."""
        ...

    def get_toolsets(self) -> list[Any]:
        """The same tools as pydantic-ai `FunctionToolset`s.

        Separate from `get_tools` because a host splits them: tools that load
        eagerly, and deferred ones (`defer_loading=True`) whose schemas are only
        fetched when the model asks. `get_tools` is the flat view the capabilities
        need to reason about metadata; `get_toolsets` is what the Agent is built with.
        """
        ...


@runtime_checkable
class AgentConfig(Protocol):
    """Answers "which model for this job?"

    A use case (`"chat"`, `"summarize"`, `"classify"`) maps to a primary model and an
    ordered fallback chain. The harness never hardcodes a model slug; the host owns
    that policy, and it is the one thing most likely to differ between hosts.
    """

    def resolve_primary(self, use_case: str) -> str:
        """The model slug to try first for this use case."""
        ...

    def resolve_fallbacks(self, use_case: str) -> Sequence[str]:
        """Ordered fallbacks, tried when the primary fails. May be empty.

        A ``Sequence`` (list or tuple) — the builder copies it, so either is fine.
        """
        ...


@runtime_checkable
class ActionGuardPolicy(Protocol):
    """Answers "what counts as a completed action, and what do we say when it wasn't?"

    The Layer-3 guard's *algorithm* is the harness's: "a mutation was attempted and
    none succeeded → the model is claiming an action it did not perform" (see
    `runtime/action_guard.py`). Its *evidence* cannot be — `send_customer_message`
    means nothing to another host — and neither can the correction text, which is
    product copy in the host's voice and language.

    This is NOT a fourth seam. It hangs off `AgentDeps` like `tool_provider` does,
    for the same reason: which tools mutate depends on who is asking, so the answer
    is a function of the run, not a constant.
    """

    def mutation_tool_names(self) -> frozenset[str]:
        """Tools whose successful return is evidence a claimed action really happened.

        Derive this from tool metadata, do not hand-write it. A hand-written list is
        a second source of truth, and this one rots silently: CRM's was **15 tools
        short**, and for every one of them the guard was blind — the model could call
        it, have it fail, announce success, and be believed. Which is the exact
        failure the guard exists to prevent.
        """
        ...

    def no_evidence_reply(self) -> str:
        """What the user sees INSTEAD of the fabricated success.

        One string, used on every transport. Streaming and sync used to carry
        different wording for the same event, so the same failure read differently
        depending on how the answer was delivered.
        """
        ...


@runtime_checkable
class AgentDeps(Protocol):
    """What the harness may assume about a host's dependency object.

    Everything else on `deps` is the host's business — the harness never touches it.
    These are the properties the machinery itself reaches for.
    """

    @property
    def tool_provider(self) -> ToolProvider:
        """Which tools this run has."""
        ...

    @property
    def action_guard_policy(self) -> ActionGuardPolicy:
        """What counts as a completed action for this run."""
        ...
