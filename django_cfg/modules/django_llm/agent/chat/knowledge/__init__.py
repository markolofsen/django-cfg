"""A knowledge base for a chat kind: a folder of markdown the model searches, outlines and reads, with citations.

    ChatKind(..., knowledge=True)                       # the folder in CHAT__KNOWLEDGE_DIR (default <BASE_DIR>/knowledge)
    ChatKind(..., knowledge="public")                   # one subfolder of it
    ChatKind(..., knowledge=lambda deps: "staff" if deps.is_staff else "public")   # per request, from what make_deps built
    ChatKind(..., knowledge=Knowledge(base=my_base, language="German"))

Default off. A missing or empty folder is also off (nothing is added to the prompt, no tool is offered). The files stay the source
of truth; the index is rebuilt in the worker when they change. See `../@docs/chat-knowledge.md`.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from django_cfg.modules.django_llm.agent.chat.knowledge.base import (
    DiskKnowledgeBase,
    Entry,
    KbError,
    KbNotFound,
    KbPathError,
    KnowledgeBase,
    Page,
    ScopedKnowledgeBase,
    StubKnowledgeBase,
)
from django_cfg.modules.django_llm.agent.chat.knowledge.index import Hit
from django_cfg.modules.django_llm.agent.chat.knowledge.check import Report, check, check_dir
from django_cfg.modules.django_llm.agent.chat.knowledge.settings import disk_base, knowledge_dir, knowledge_language, warn_missing, warn_once
from django_cfg.modules.django_llm.agent.chat.knowledge.tools import Caps, KbSession, guard_note, make_tools, prompt_block
from django_cfg.modules.django_llm.agent.chat.knowledge.tree import render_tree

log = logging.getLogger(__name__)

__all__ = [
    "Caps", "DiskKnowledgeBase", "Report", "check", "check_dir", "Entry", "Hit", "KbError", "KbNotFound", "KbPathError", "KbSession", "Knowledge", "KnowledgeBase",
    "KnowledgeRuntime", "Page", "ScopedKnowledgeBase", "StubKnowledgeBase", "render_tree", "resolve", "runtime",
]


@dataclass(frozen=True)
class Knowledge:
    """The explicit form of `ChatKind.knowledge`. `source`: `True` (the configured folder), a subfolder name, an absolute `Path`
    (its own folder) or any `KnowledgeBase`."""

    source: Any = True
    language: str | None = None  # the language the files are written in; default CHAT__KNOWLEDGE_LANGUAGE, else English
    caps: Caps = field(default_factory=Caps)
    guard: bool = True  # append a note when the answer cites a file this answer never opened
    tool_prefix: str = "kb_"  # tool names are `<prefix>tree|search|outline|read`; set it when a host tool already uses `kb_search` ...


Spec = Any  # None | bool | str | Path | KnowledgeBase | Knowledge | Callable[[deps], Spec]


@dataclass
class KnowledgeRuntime:
    session: KbSession
    prompt: str
    tools: list[Callable[..., Any]]
    guard: bool
    prefix: str = "kb_"

    def tool_names(self) -> list[str]:
        return [t.name for t in self.tools]

    def note_for(self, answer: str) -> str:
        if not self.guard:
            return ""
        missing = self.session.unopened(answer)
        return guard_note(missing) if missing else ""


def _base_for(source: Any) -> KnowledgeBase | None:
    if source is None or source is False:
        return None
    if isinstance(source, KnowledgeBase):
        return source
    if source is True:
        root = knowledge_dir()
        if not root:
            warn_missing()
            return None
        return disk_base(root)
    if isinstance(source, Path) or (isinstance(source, str) and Path(source).is_absolute()):
        if Path(source).is_dir():
            return disk_base(source)
        warn_once(f"chat knowledge: folder {source} does not exist; the kind answers without a knowledge base (is it copied into the image?)")
        return None
    if isinstance(source, str):
        root = knowledge_dir()
        if not root:
            warn_missing()
            return None
        return ScopedKnowledgeBase(disk_base(root), source)
    raise TypeError(f"ChatKind.knowledge: unsupported source {source!r}")


def resolve(spec: Spec, deps: Any) -> tuple[KnowledgeBase, Knowledge] | None:
    """The base and settings a kind uses for this request, or `None` (off). A callable gets the kind's deps."""
    if callable(spec) and not isinstance(spec, KnowledgeBase | Knowledge):
        spec = spec(deps)
    knowledge = spec if isinstance(spec, Knowledge) else Knowledge(source=spec)
    source = knowledge.source
    if callable(source) and not isinstance(source, KnowledgeBase):
        source = source(deps)
    base = _base_for(source)
    return (base, knowledge) if base is not None else None


def runtime(spec: Spec, deps: Any) -> KnowledgeRuntime | None:
    """Everything one answer needs: the prompt block, the tools bound to a fresh budget, the guard. `None` when off or empty.
    A knowledge base that fails here is logged and the chat goes on without it."""
    try:
        found = resolve(spec, deps)
        if found is None:
            return None
        if not found[0].entries():
            warn_once(f"chat knowledge: the knowledge base is empty ({found[0].__class__.__name__}); the kind answers without it")
            return None
        base, knowledge = found
        prefix = knowledge.tool_prefix
        session = KbSession(base, knowledge.caps, prefix=prefix)
        return KnowledgeRuntime(
            session, prompt_block(base, knowledge.language or knowledge_language(), knowledge.caps, prefix), make_tools(session), knowledge.guard, prefix,
        )
    except Exception:  # noqa: BLE001 - a broken knowledge base must not stop the chat
        log.exception("chat: knowledge base unavailable, answering without it")
        return None
