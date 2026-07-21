"""The base dependency object a host subclasses — the generic half of `deps`.

Every pydantic-ai tool in a run receives one `deps`. Most of what's on it is the
host's business (a CRM run carries a user, a session, a project, RAG results…), and
the harness never touches those. But a handful of fields ARE the harness's: the
conversation history, the per-turn tool-call counters the call-cap capability reads,
the sandbox set the toolset builder reads, the search context. Those live here, so
they are defined once and every host inherits them rather than re-declaring them.

A host subclasses this and adds its own fields:

    @dataclass
    class ChatAgentDeps(AgentDeps):
        user: Any = None
        session: Any = None
        ...

and overrides the two property HOOKS (`tool_provider`, `action_guard_policy`) to
return its seam implementations. The base leaves them raising `NotImplementedError`,
so a host that forgets one fails loudly at first use rather than silently degrading.

**Every field here has a default.** That is not cosmetic: a dataclass subclass cannot
add a non-default field after an inherited default one, so a defaulted base is what
lets a host declare required-looking fields of its own. All construction is by
keyword regardless, so the field order is not a positional contract.

This satisfies `agent/protocols.py::AgentDeps` structurally. The Protocol is the
minimum the harness reaches for; this base is the concrete generic implementation of
it plus the shared plumbing.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class AgentDeps:
    """Generic run dependencies. Hosts subclass and add their own fields."""

    # The conversation so far, as [{role, content}, …]. The harness converts it to
    # pydantic-ai ModelMessages; the host decides how it was assembled.
    history: list[dict] = field(default_factory=list)

    # The host's settings object (model choice, limits). Opaque to the harness — it
    # is handed to the host's own model resolver, never read here.
    settings: Any = None

    # Run budgets the search context enforces.
    max_tool_calls: int = 10
    max_rag_searches: int = 3

    # Lazily-built per-run search/dedup context. `get_search_ctx()` populates it.
    search_ctx: Optional[Any] = None

    # Names of the read-only tools CodeMode will run inside `run_code`, so the
    # toolset builder hands those over as their structured sandbox projection. Set by
    # the runner before the first `get_toolsets()`. Empty = no sandbox this run.
    # ONLY reads belong here — a mutation inside the sandbox never passed HITL.
    _sandboxed: frozenset[str] = frozenset()

    # Per-turn tool-call counters, keyed by tool name. deps is rebuilt each turn, so
    # this resets every turn. The per-turn call cap reads it to drop a tool that the
    # model keeps re-calling with empty args.
    _tool_call_counts: dict[str, int] = field(default_factory=dict)

    def bump_tool_call(self, name: str) -> int:
        """Increment and return the per-turn call count for ``name``."""
        count = self._tool_call_counts.get(name, 0) + 1
        self._tool_call_counts[name] = count
        return count

    def tool_call_count(self, name: str) -> int:
        """Return the per-turn call count for ``name`` without bumping it.

        The ``prepare_tools`` backstop uses it to decide whether a tool has been
        over-called this turn and should be dropped from the next model request — a
        tool *result* cannot reliably stop a model from re-calling, so the tool is
        removed from the surface instead.
        """
        return self._tool_call_counts.get(name, 0)

    def get_search_ctx(self) -> Any:
        """Return the run's search context, building it on first use.

        The concrete class is generic (a counter/dedup helper); its default budgets
        come from a host config, so the host may override this to inject those. The
        base builds a plain context from the two ``max_*`` fields.
        """
        if self.search_ctx is None:
            from modules.django_llm.agent.bus.context import AgentSearchContext

            self.search_ctx = AgentSearchContext(
                max_searches=self.max_rag_searches,
                max_tool_calls=self.max_tool_calls,
            )
        return self.search_ctx

    # ── Seam hooks — a host MUST override these ──────────────────────────────────
    #
    # They are properties, not fields, because the seam they return is often built
    # from `self` (a ToolProvider closes over these deps). The base raises rather
    # than returning a stub: a stubbed provider returning [] would let the harness
    # classify every tool as a read and silently stop capping mutations — a loud
    # failure is the correct one.

    @property
    def tool_provider(self) -> Any:
        """The run's `ToolProvider` — which tools this run has. Host-supplied."""
        raise NotImplementedError(
            f"{type(self).__name__} must override `tool_provider` to return its "
            "ToolProvider (see agent/protocols.py). The harness has no way to know "
            "which tools a host's run should have."
        )

    @property
    def action_guard_policy(self) -> Any:
        """The run's `ActionGuardPolicy` — what counts as a completed action.

        May return ``None`` if a host does not run the Layer-3 guard; the streaming
        loop treats a ``None`` policy as "guard disabled". Overriding is therefore
        optional, unlike ``tool_provider``.
        """
        return None
