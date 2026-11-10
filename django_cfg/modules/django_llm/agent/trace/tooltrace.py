"""What a tool says about itself to the trace: its label, role and the views it allows out.

A tool with no declaration records its name and outcome only (`redaction="omitted"`): the safe default, and the one a public
chat wants. A declaration is the tool author's statement that these arguments and this result text may be shown to the person
the chat belongs to. `ChatKind.trace_tools` maps a tool name to its `ToolTrace`.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any

from django_cfg.modules.django_llm.agent.trace.step import StepRef, StepStatus, ToolRole, TraceErrorCode

#: `ToolMeta.category` -> the role a step of that tool carries, unless the declaration names one.
ROLE_BY_CATEGORY: dict[str, ToolRole] = {
    "kb_read": ToolRole.RETRIEVER,
    "read": ToolRole.READ,
    "profile": ToolRole.READ,
    "url_builder": ToolRole.READ,
    "conversation": ToolRole.READ,
    "outbound_query": ToolRole.READ,
    "outbound_propose": ToolRole.PROPOSE,
    "outbound_confirm": ToolRole.WRITE,
    "outbound_cancel": ToolRole.WRITE,
    "mutation": ToolRole.WRITE,
}


@dataclass(frozen=True)
class Verdict:
    """What a tool's result text says about the call when it did not simply work: a refusal is `SKIPPED`, a failure `ERROR`.
    `code` is from the closed vocabulary (`LIMIT` for a cap the tool hit); the text itself is never kept."""

    status: StepStatus
    code: TraceErrorCode | None = None


@dataclass(frozen=True)
class ToolTrace:
    """The declared view of one tool. Every callable runs on the server, on the raw call, and may not raise (a raise drops the detail).

    A step keeps ids, counts and the declared views, never the text a tool returned: `summary` is one line ("3 documents"), `refs` the
    ids the call used, `verdict` a refusal read from the result ("search limit reached" is `SKIPPED`, not `OK`). A tool whose answer
    depends on the run's own state (the hits it showed under numbers, the draft it opened) sets `with_deps`: `summary`, `refs` and
    `verdict` then take `(args, result text, deps)`, the deps the run was built with.
    """

    label: str  # "Searching the knowledge base"
    role: ToolRole | None = None  # default: from `ToolMeta.category`, else `read`
    summary: Callable[..., str] | None = None  # (args, result text) -> "5 documents"
    args: Sequence[str] | Callable[[dict], dict] | None = None  # keys of the arguments that may be shown, or a function that returns the view
    result: bool | Callable[[str], str] = False  # True: the start of the result text may be shown; a function returns the view
    refs: Callable[..., Sequence[StepRef]] | None = None  # (args, result text) -> what the call used (documents, records)
    verdict: Callable[..., Verdict | None] | None = None  # (args, result text) -> a refusal or failure the text reports; None: the call worked
    with_deps: bool = False  # `summary`, `refs` and `verdict` also receive the run's deps as a third argument
    query_arg: str | None = None  # the argument that holds the search text (shown as `query` at level 2)

    def view_args(self, raw: dict) -> dict | None:
        if self.args is None:
            return None
        if callable(self.args):
            return dict(self.args(raw))
        return {k: raw[k] for k in self.args if k in raw}

    def call(self, fn: Callable[..., Any], raw: dict, text: str, deps: Any) -> Any:
        return fn(raw, text, deps) if self.with_deps else fn(raw, text)

    def view_result(self, text: str) -> str | None:
        if self.result is False:
            return None
        return text if self.result is True else str(self.result(text))


def generic_label(name: str) -> str:
    """`kb_search` -> "Kb search": a readable fallback so a step is never blank. Never a raw `mcp__` name."""
    bare = name.rsplit("__", 1)[-1]
    return bare.replace("_", " ").strip().capitalize()


def role_for(name: str, declared: ToolTrace | None, categories: dict[str, str]) -> ToolRole:
    if declared is not None and declared.role is not None:
        return declared.role
    return ROLE_BY_CATEGORY.get(categories.get(name, ""), ToolRole.READ)


def raw_args(args: Any) -> dict:
    return args if isinstance(args, dict) else {}
