"""What a tool says about itself to the trace: its label, role and the views it allows out.

A tool with no declaration records its name and outcome only (`redaction="omitted"`): the safe default, and the one a public
chat wants. A declaration is the tool author's statement that these arguments and this result text may be shown to the person
the chat belongs to. `ChatKind.trace_tools` maps a tool name to its `ToolTrace`.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any

from django_cfg.modules.django_llm.agent.trace.step import StepRef, ToolRole

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
class ToolTrace:
    """The declared view of one tool. Every callable runs on the server, on the raw call, and may not raise (a raise drops the detail)."""

    label: str  # "Searching the knowledge base"
    role: ToolRole | None = None  # default: from `ToolMeta.category`, else `read`
    summary: Callable[[dict, str | None], str] | None = None  # (args, result text) -> "5 documents"
    args: Sequence[str] | Callable[[dict], dict] | None = None  # keys of the arguments that may be shown, or a function that returns the view
    result: bool | Callable[[str], str] = False  # True: the start of the result text may be shown; a function returns the view
    refs: Callable[[dict, str | None], Sequence[StepRef]] | None = None  # what the call used (documents, records)
    query_arg: str | None = None  # the argument that holds the search text (shown as `query` at level 2)

    def view_args(self, raw: dict) -> dict | None:
        if self.args is None:
            return None
        if callable(self.args):
            return dict(self.args(raw))
        return {k: raw[k] for k in self.args if k in raw}

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
