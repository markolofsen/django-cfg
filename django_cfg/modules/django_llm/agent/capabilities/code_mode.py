"""CodeMode — let the model write Python that calls the CRM's read tools.

An analytical question ("overdue tasks for clients who wrote this week, ranked
by workload") is a fan-out plus an aggregate. As native tool calls that is
``query_customers`` -> N x ``get_client_tasks`` -> aggregate: five to eight
round-trips, with **every intermediate row landing in the context window**.

``CodeMode`` collapses it into one ``run_code`` call. The model writes Python
that calls our tools as functions -- loops, ``asyncio.gather``, filtering and
ranking all happen inside a `Monty <https://github.com/pydantic/monty>`_ sandbox
(a Rust interpreter behind pyo3, not ``exec()``), and only the answer comes back.
The rows never enter the transcript, which is a PII win as much as a token one.

Two choices here are load-bearing.

**Only reads are sandboxed.** ``tools='all'`` would fold the mutations in too,
and a ``propose_send_customer_message`` fired from inside a sandbox loop is a
customer-visible send that never passed the HITL approval round-trip. Mutations
stay native, where ``requires_approval=True`` can suspend the run. This module
therefore takes an explicit allow-list; it never infers one.

**Sandboxed tools return data, not prose.** A CRM tool's native callable returns
``llm_text`` -- a display string with the structured payload hidden behind a
sentinel. Model code cannot index that (``TypeError: str indices must be
integers``), and worse, ``CodeMode`` renders each tool's declared return type
into the function catalog it shows the model, so a tool advertising ``-> str``
teaches the model to write string handling and it never attempts the loop.
``BaseTool.as_sandbox_callable`` is the projection that returns the rows; see
``ai/tools/core/_base_tool.py``.
"""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from dataclasses import dataclass, field
from typing import Any, Literal

from pydantic_ai.exceptions import UserError
from pydantic_ai_harness.code_mode import CodeMode
from pydantic_ai_harness.code_mode._toolset import CodeModeToolset
from pydantic_monty import ResourceLimits

# The analytical read surface -- the tools an operator's "find X, then for each
# of them Y, ranked by Z" question actually chains through. These are the tools
# paid for on every turn (the deferred sets cost nothing until ``search_tools``
# reveals them), and they are the ones that fan out.
#
# Mutations are deliberately absent. So are the deferred tools: ``CodeMode``
# leaves a deferred tool hidden until it is loaded, so they compose without
# needing to be named here.
SANDBOXED_READ_TOOLS: frozenset[str] = frozenset({
    # Client reads -- the fan-out roots.
    "list_clients",
    "lookup_client",
    "query_customers",
    "search_clients_semantic",
    "get_client_tasks",
    "get_client_history",
    "get_client_timeline",
    "get_client_notes",
    "get_client_links",
    "get_client_onboarding",
    "find_duplicate_clients",
    # Task reads -- what the fan-out lands on.
    "list_tasks",
    "get_task",
    "check_task_conflicts",
    "find_similar_tasks",
    # Conversation reads.
    "search_conversations",
    "get_conversation_thread",
    "get_customer_open_ticket",
    "suggest_reply_from_similar_tickets",
    # Org / staff reads. Small, but they were the loop bait -- see below.
    "list_staff",
    "get_org_overview",
    "get_org_activity",
    "get_user_machines",
    "get_user_instances",
    "list_message_attachments",
})
"""Every analytical read goes in the sandbox, not just the fan-out roots.

The first version of this list held only the twelve tools a fan-out chains
through, and left the other sixteen reads on the native surface. A live e2e run
showed why that is worse than either extreme:

Asked to close some overdue tasks, the model was offered 52 tools. ``list_tasks``
was **not** among them (sandboxed), but ``list_documents``, ``list_staff`` and
``list_message_attachments`` were. So it called those -- over and over -- and never
touched a task. That is not a weak model making a dumb choice; it is a **rational**
one. The tools it could see were one cheap call away, and the tool it needed was
buried in an 11 589-character ``run_code`` description it would have to read and
then write Python against.

Half-sandboxing is the worst of both worlds: the useful reads are hidden and the
useless ones are not. Either the reads are behind ``run_code`` or they are not.

Deliberately still native:

- ``search_knowledge_base`` / ``contextual_search`` / ``get_document`` /
  ``get_chunk_context`` -- RAG. The model uses these to ground an answer, not to
  fan out over rows, and their results are meant to land in its context.
- ``download_user_file`` / ``transcribe_voice_note`` -- these have side effects
  (fetch, transcode). They are not reads in the sense that matters here.
"""


def _default_resource_limits() -> ResourceLimits:
    """Backstop sandbox limits for one ``run_code`` execution.

    The first two are the harness's own backstop, lifted verbatim from the sibling
    capability that already solved this (``dynamic_workflow/_toolset.py``,
    ``_default_resource_limits``). The third is the one it deliberately leaves unset
    and we deliberately set.

    ``max_duration_secs`` is **the only thing standing between a model-written
    ``while True:`` and a worker that never comes back.** None of the obvious guards
    catch it:

    - ``asyncio.wait_for`` cannot. Monty runs the loop in Rust and never yields to the
      event loop, so the timeout does not fire -- verified: an 8s ``wait_for`` around a
      ``while True:`` was still running a minute later.
    - ``UsageLimits(request_limit=...)`` cannot. That caps *model* round-trips; a
      runaway is a single ``run_code`` call, so there is never a second request to
      refuse.

    Monty enforces it per bytecode step, which is why it works where those do not.
    Time spent awaiting our tools does **not** count against it -- during an ``await``
    the sandbox is suspended and no sandbox code runs -- so this bounds the model's own
    computation, not how slow the CRM is. 20s is generous for a fan-out-and-rank and
    ruinous for an infinite loop.

    ``DynamicWorkflow`` leaves it unset because its sandbox orchestrates sub-agents and
    an honest script legitimately runs for minutes. ``run_code`` filters and ranks rows;
    it has no honest reason to.
    """
    return {
        "max_memory": 256 * 1024 * 1024,
        "max_allocations": 50_000_000,
        "max_duration_secs": 20.0,
    }


# ``ResourceLimits`` is ``total=False``, so a typo (``max_durations_secs``) would merge
# through and silently drop the guard. Upstream rejects unknown keys for exactly this
# reason (``dynamic_workflow/_toolset.py:_RESOURCE_LIMIT_KEYS``); so do we.
_RESOURCE_LIMIT_KEYS = frozenset(ResourceLimits.__annotations__)


def _resolve_resource_limits(
    limits: ResourceLimits | Literal["unlimited"] | None,
) -> ResourceLimits:
    """Resolve the public ``resource_limits`` value to what the sandbox is handed.

    ``None`` applies the backstop; ``'unlimited'`` removes every cap; a partial mapping
    merges *onto* the backstop rather than replacing it, so ``{'max_memory': ...}`` cannot
    silently drop the duration guard. Same three-way contract as
    ``DynamicWorkflow.resource_limits`` -- one semantics for both sandboxes.
    """
    if limits is None:
        return _default_resource_limits()
    if limits == "unlimited":
        return {}
    unknown = set(limits) - _RESOURCE_LIMIT_KEYS
    if unknown:
        raise UserError(
            f"Unknown `resource_limits` key(s): {sorted(unknown)}. "
            f"Valid keys are {sorted(_RESOURCE_LIMIT_KEYS)}."
        )
    return {**_default_resource_limits(), **limits}


def _reads_only_note(write_tools: Sequence[str] | None) -> str:
    """The "writes don't exist in the sandbox" bullet — host-parametrised.

    The *fact* is the harness's (a read-only sandbox is what ``CodeMode`` is for);
    the *example tool names* are the host's. Baking CRM names here would lie to a
    model in django-cfg, whose write tools are named differently — the one CRM leak
    left in a harness prompt string (Phase 10). When the host names some write tools
    the bullet cites two of them concretely; when it names none the bullet still
    stands, just without the examples.
    """
    examples = ""
    if write_tools:
        shown = ", ".join(f"`{t}`" for t in list(write_tools)[:4])
        examples = f" (for example {shown})"
    return (
        f"- **Reads only — the write tools do not exist in here.** The write tools"
        f"{examples} are not defined inside the sandbox, and calling one is a "
        "`NameError` that throws away everything you just read. Only the functions "
        "listed below exist. Use this call to *read* and end it with the ids you "
        "need; then issue the write as an ordinary tool call, outside `run_code`, in "
        "your next step."
    )


#: The sandbox-language notes that name no host tool — pure Monty/type-checker facts.
#: The reads-only bullet that DID name CRM tools is now ``_reads_only_note`` (built
#: from host-supplied names); these three are host-agnostic and always rendered.
SANDBOX_LANGUAGE_NOTES = """
- **No `next()`.** It is not defined here, in any form -- the sandbox's type checker \
rejects the snippet before a line of it runs (`Name 'next' used when not defined`), \
so `next(rows)`, `next(iter(rows))` and `next((r for r in rows if ...), None)` all \
fail alike. To take the first match, filter into a list and index it: \
`hits = [r for r in rows if ...]` then `hits[0] if hits else None`. \
`len`, `sorted`, `sum`, `min`, `max`, `any`, `all`, `enumerate`, `zip` and \
list/dict comprehensions all behave normally.
- **The date needs an import, every time.** The clock is available, but `datetime` is \
still an ordinary module: `today = date.today()` after `from datetime import date` -- \
or `import datetime` first if you want to write `datetime.date.today()`. Reaching \
straight for `datetime.date.today()` with no import is `Name 'datetime' used when not \
defined`, and it is the single commonest way to lose a snippet here, because most CRM \
questions are about time.
- **Call the tools by their bare names.** They are already in scope: \
`await list_tasks(...)`, not `await default_api.list_tasks(...)` and not \
`await tools.list_tasks(...)`. There is no module to reach through, and inventing one \
is `Name 'default_api' used when not defined`.\
"""
"""The restrictions ``run_code``'s description has to carry, and upstream does not.

Every one of these was found the same way: a live trace showed the model writing it,
losing the snippet, and spending an attempt to recover. They are ordered by how often
that happened.

The last two share a root. Upstream's description promises
"``datetime.datetime.now()`` and ``datetime.date.today()`` are routed to the OS
handler", which reads like they are *ready to use* -- so the model writes
``datetime.date.today()`` and gets ``Name 'datetime' used when not defined``, because
the neighbouring bullet's "these must be imported before use" applies to ``datetime``
too. Both statements are true and together they mislead. Since we hand the sandbox a
clock (see ``_clock_only_os``) precisely because CRM questions are about time, the
model reaches for the date constantly, and this fired more than anything else.
``default_api.list_tasks(...)`` is the same instinct in the other direction: reaching
through a module that is not there.

Upstream already lists the sandbox's limits right here — "No classes", "No
third-party libraries", "No ``import *``" (``code_mode/_toolset.py``,
``_RUN_CODE_DESCRIPTION_HEAD``/``_TAIL``). These two join them.

**Why the description and not the system prompt.** This is the lesson that cost the
most. ``ADMIN_TOOL_FLOW`` has said "writes are not available inside ``run_code``"
for the whole of this work, in bold, with an example — and the model kept writing
``await update_tasks(...)`` in the sandbox anyway, roughly once a run, losing the
turn's read when it did. A system-prompt note is read once, at the top of the turn,
and is gone by the time the model is composing a snippet. **The tool description is
what it reads at the moment it decides to write code.** That is upstream's own
convention for exactly this class of restriction, and both of these belong there.

The ``next`` one: "find the first row that matches" is the commonest thing a fan-out
does, and ``next(...)`` is the first idiom every model reaches for::

    user = next((s for s in staff['rows'] if s['email'] == email), None)

**``next`` is not in Monty's type checker.** Its vendored typeshed defines
``__next__`` and ``SupportsAnext`` but no ``next`` builtin (checked against monty
0.0.19-beta.4 -- this is not about to fix itself), so the static pass rejects *any*
use of the name with ``Name `next` used when not defined`` before a line executes.
Not the generator form -- the name.

Two layers of trap, and it matters that they are separate:

1. The type checker refuses ``next`` outright. This is what actually fires.
2. Underneath it, Monty's generator expressions are not lazy -- they materialise into
   a ``list`` -- so even if the checker knew ``next``, the generator form would raise
   ``TypeError: 'list' object is not an iterator`` at runtime.

An earlier version of this note described only (2) and told the model
"``next(iter(rows))`` works". It does not: (1) refuses it. That note was itself a lie
in the tool surface -- the exact failure it was written to prevent -- and the model
duly read it, reached for ``next``, and burned a retry. It now says the true thing:
``next`` does not exist here, in any form.

A tempting wrong turn, for the record: declaring a ``next`` stub so the type checker
stops rejecting it. That makes it *worse* -- the code then type-checks and blows up at
runtime on (2) instead of being refused up front. A door into a wall.
"""


def _sandbox_notes(write_tools: Sequence[str] | None) -> str:
    """The full sandbox-language block: the host-parametrised reads-only bullet
    first (it is the one the model most needs and the only host-specific line),
    then the three host-agnostic Monty facts."""
    return "\n" + _reads_only_note(write_tools) + SANDBOX_LANGUAGE_NOTES


@dataclass
class _LimitedCodeModeToolset(CodeModeToolset):
    """``CodeModeToolset`` whose sandbox carries resource limits and our language notes.

    Two overrides, and the seams they use are not symmetric -- check before adding a
    third.

    **``resource_limits`` -> the REPL constructor.** ``CodeMode`` builds its REPL bare
    (``self._repl = MontyRepl()``, ``_toolset.py:539``) and exposes no way in: ``mount``
    and ``os_access`` are capability arguments, limits are not. They have to reach the
    *constructor* -- ``feed_start`` and ``resume`` do not take them -- so we intercept the
    assignment. ``_repl`` becomes a property whose setter rebuilds a fresh REPL with
    limits, and passes ``None`` straight through.

    That ``None`` is load-bearing. The tempting shortcut -- pre-filling the ``_repl``
    field -- **silently disables type checking**: upstream gates it on
    ``fresh_repl = self._repl is None`` (``_toolset.py:435``), so a pre-filled field
    means the model's first snippet is never type-checked and the pass that catches a
    bad call signature before any code runs is gone. Passing ``None`` through keeps
    ``fresh_repl`` flipping exactly as upstream expects.

    Delete this half the day ``CodeMode`` accepts limits directly -- and it should:
    ``DynamicWorkflow``, in the same package, already does (``MontyRepl(limits=limits)``,
    ``dynamic_workflow/_toolset.py:679``). ``CodeMode`` simply never wired it up.

    **``_build_description`` -> the sandbox's own restrictions.** Upstream splices its
    restrictions ("No classes", "No third-party libraries") between a HEAD and a TAIL and
    appends the tool catalog after. Ours have to land in that same prose, *before* the
    catalog -- string-appending to the finished description would strand them after
    several thousand characters of function signatures, where nobody reads them,
    including an LLM. So rebuild from upstream's own pieces.

    Overriding this is safe *because* ``get_tools`` calls it through ``self``
    (``_toolset.py:380``), even though upstream declares it a ``@staticmethod``. Its
    sibling ``_build_type_check_stubs`` is **not** safe to override: ``_type_check``
    calls it as ``CodeModeToolset._build_type_check_stubs(...)``, hard-coded to the base
    class (``_toolset.py:723``), so a subclass override there is never reached.
    """

    resource_limits: ResourceLimits | Literal["unlimited"] | None = None
    """Sandbox limits for one ``run_code`` execution. See ``_resolve_resource_limits``."""

    write_tool_names: tuple[str, ...] = ()
    """Host-supplied names of the write tools, for the reads-only bullet's examples.
    Empty is fine — the bullet still stands, just without concrete names. See
    ``_reads_only_note``; this is what keeps CRM tool names out of the harness prompt."""

    @property
    def _repl(self):  # type: ignore[override]
        return self.__dict__.get("_limited_repl")

    @_repl.setter
    def _repl(self, value) -> None:
        from pydantic_monty import MontyRepl

        if value is not None:
            value = MontyRepl(limits=_resolve_resource_limits(self.resource_limits))
        self.__dict__["_limited_repl"] = value

    def _build_description(self, callable_defs, *, has_os: bool, has_mount: bool) -> str:  # type: ignore[override]
        from pydantic_ai_harness.code_mode._toolset import _base_description

        base = _base_description(has_os=has_os, has_mount=has_mount) + _sandbox_notes(
            self.write_tool_names,
        )
        catalog = CodeModeToolset._render_catalog(callable_defs)
        return base + "\n\n" + catalog if catalog else base

    async def call_tool(self, name, tool_args, ctx, tool):  # type: ignore[override]
        """Upstream's ``call_tool``, plus the one Monty error it forgets to catch.

        A construct Monty has not implemented -- a ``class`` is the one the model
        actually writes -- surfaces from the **type-check** pass as a
        ``MontyRuntimeError`` wrapping ``NotImplementedError``. Upstream's
        ``_type_check`` catches only ``MontyTypingError`` and ``MontySyntaxError``
        (``_toolset.py:726``), so it escapes ``call_tool`` entirely and **kills the
        whole agent run**.

        That is a bad trade for a construct upstream's own description already forbids
        ("No classes"): the model wrote something it was told not to, which is worth a
        retry, not the turn. Two live e2e scenarios died this way -- as
        ``NotImplementedError``, with no trace of what the model had written.

        Note the asymmetry that hides it: the *execution* path is fine. The same class
        definition reaching ``feed_start`` comes back as a plain ``MontyRuntimeError``,
        which upstream does catch and turn into a ``ModelRetry``. Only the type-check
        pass, which runs first and only on a fresh REPL, leaks it.
        """
        from pydantic_ai import ModelRetry
        from pydantic_monty import MontyRuntimeError

        try:
            return await super().call_tool(name, tool_args, ctx, tool)
        except MontyRuntimeError as exc:
            # Upstream already converts these on the execution path; this only fires
            # for the type-check pass, which does not.
            raise ModelRetry(f"Unsupported code:\n{exc}") from exc


@dataclass
class _LimitedCodeMode(CodeMode):
    """``CodeMode`` that hands the sandbox resource limits.

    ``get_wrapper_toolset`` is the capability's own extension point, so this needs no
    fork and no patching of upstream's module namespace. The public field mirrors
    ``DynamicWorkflow.resource_limits`` exactly -- same name, same three-way contract --
    so if upstream ever lands this on ``CodeMode``, the call sites here do not change.
    """

    resource_limits: ResourceLimits | Literal["unlimited"] | None = field(
        default=None, kw_only=True
    )
    """Sandbox limits guarding the model's own computation inside ``run_code``.

    ``None`` applies the backstop (256 MB, 50M allocations, 20s); ``'unlimited'`` removes
    every cap; a partial mapping merges onto the backstop, overriding only the caps it
    names. Unknown keys raise rather than being silently dropped.
    """

    write_tool_names: tuple[str, ...] = field(default=(), kw_only=True)
    """Host-supplied write-tool names, surfaced in the reads-only bullet's examples.
    Threaded to ``_LimitedCodeModeToolset``; keeps CRM names out of the harness prompt."""

    def get_wrapper_toolset(self, toolset):  # type: ignore[override]
        return _LimitedCodeModeToolset(
            wrapped=toolset,
            tool_selector=self.tools,
            max_retries=self.max_retries,
            dynamic_catalog=self.dynamic_catalog,
            os_access=self.os_access,
            mount=self.mount,
            resource_limits=self.resource_limits,
            write_tool_names=self.write_tool_names,
        )


def _clock_only_os(fn: Any, args: Any, kwargs: Any) -> Any:
    """Answer the sandbox's clock calls. Refuse every other OS call.

    Monty gives sandboxed code no wall clock by default -- ``date.today()`` and
    ``datetime.now()`` raise. That is the right default for untrusted code, and it
    was wrong for a CRM: half the questions an operator asks are *about time*
    ("what's overdue", "what's due today"), so the model has to know what day it
    is to answer them.

    Without this, both models we tried burned all three ``run_code`` retries trying
    to find a clock -- ``date.today()``, then ``datetime.utcnow()``, then
    ``datetime.now()`` -- and the turn died with ``exceeded max retries``. It read
    like a weak model failing; it was our sandbox withholding the date.

    Only the clock is answered. Filesystem and environment calls return
    ``NOT_HANDLED``, which makes them fail inside the sandbox exactly as they do
    today. See ``code_mode/README.md`` -- "``datetime.now()`` / ``date.today()``
    become available with an ``os_access`` handler".
    """
    from datetime import date, datetime
    from pydantic_monty import NOT_HANDLED

    if fn == "date.today":
        return date.today()
    if fn == "datetime.now":
        # Naive local time: the CRM's own date fields are naive, so handing the
        # sandbox an aware datetime would make `task['due_date'] < now` raise.
        return datetime.now()
    return NOT_HANDLED


def build_code_mode_capability(
    *,
    tool_names: Sequence[str] | None = None,
    write_tool_names: Sequence[str] | None = None,
) -> CodeMode:
    """Assemble the ``CodeMode`` capability over the analytical read tools.

    ``tool_names`` overrides the allow-list; it exists for tests and for a host
    project that registers its own read tools through ``ProjectToolRegistry``.
    Passing a name that is not on the agent's toolset is harmless -- the selector
    simply never matches it.

    ``write_tool_names`` are the host's WRITE tools — used only to make the
    reads-only bullet in ``run_code``'s description name two of them concretely,
    instead of the harness hardcoding CRM names in a prompt string another host will
    read (Phase 10). Purely cosmetic to the sandbox; they are never in its scope.

    ``dynamic_catalog`` stays ``False``: it earns its keep only when paired with
    ``ToolSearch``, where a mid-run discovery would otherwise bust the
    prompt-prefix cache by rewriting ``run_code``'s description. Our toolset is
    fixed per request, so the default keeps the system prompt shorter.

    No ``mount``, and ``os_access`` answers **only the clock** -- no filesystem, no
    environment (see ``_clock_only_os``; the date is load-bearing for a CRM, since
    "overdue" and "due today" are the questions operators actually ask). Sandboxed
    code reaches the CRM only through the tools passed to it, which keep enforcing
    their own ``before_call`` permission checks -- the sandbox adds a boundary, it
    does not remove one.

    ``max_retries`` stays at upstream's 3. Raising it looks free -- a retry writes
    nothing and costs one round-trip -- and it is not: a sandbox retry also spends a
    request against the turn's ``UsageLimits(request_limit=15)``
    (``runtime/streaming.py``). At 5, one bad snippet can eat a third of the turn's
    entire budget before the agent reaches the *write* the operator actually asked
    for. The retry budget is not the place to absorb a bad tool surface; a snippet
    that fails three times is telling you the surface is wrong, and the e2e trace
    will say how. Every sandbox failure we chased turned out to be ours -- a lie in a
    schema, a restriction the model was never told -- and each was fixed at the
    source, not padded around.

    And resource limits, which upstream's ``CodeMode`` does not give us -- see
    ``_default_resource_limits`` and ``_LimitedCodeMode``.
    """
    names = frozenset(tool_names) if tool_names is not None else SANDBOXED_READ_TOOLS
    return _LimitedCodeMode(
        tools=sorted(names),
        os_access=_clock_only_os,
        write_tool_names=tuple(write_tool_names or ()),
    )


def iter_sandboxed_calls(part: object) -> Iterator[tuple[str, str, Any]]:
    """Yield the (call, return) pairs a ``run_code`` execution made inside the sandbox.

    ``CodeMode`` folds N reads into one ``run_code`` call, so the model issues no
    native tool call for any of them -- they happen inside Monty. Anything that
    reconstructs "which tools ran" from the message history therefore sees only
    ``run_code`` and concludes, wrongly, that the agent did nothing.

    The harness does keep them: every nested call and return is attached to the
    ``run_code`` ``ToolReturnPart.metadata`` as
    ``{'code_mode': True, 'tool_calls': {...}, 'tool_returns': {...}}``, keyed by
    ``tool_call_id`` (``code_mode/_toolset.py:608``). This unwraps that.

    It lives here, next to the capability whose metadata format it reads, because
    it has two consumers in different layers -- the SSE runtime (to rebuild the
    admin UI's tool bubbles and the persisted ``ChatMessage.tool_calls``) and the
    e2e harness (to see through the sandbox when asserting on a run). Neither
    layer should own the other's copy.

    Yields ``(tool_name, args_repr, return_part)``. ``return_part`` is ``None``
    when a call raised inside the sandbox before producing a result.
    """
    meta = getattr(part, "metadata", None)
    if not isinstance(meta, dict) or not meta.get("code_mode"):
        return
    calls = meta.get("tool_calls") or {}
    returns = meta.get("tool_returns") or {}
    if not isinstance(calls, dict):
        return
    for call_id, call_part in calls.items():
        raw_args = getattr(call_part, "args", None)
        args_repr = (
            raw_args if isinstance(raw_args, str)
            else ("" if raw_args is None else str(raw_args))
        )
        yield (
            getattr(call_part, "tool_name", ""),
            args_repr,
            returns.get(call_id) if isinstance(returns, dict) else None,
        )
