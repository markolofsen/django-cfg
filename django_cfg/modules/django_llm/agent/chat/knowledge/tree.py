"""The folder tree as text: for the stable system-prompt prefix and for `kb_tree`.

Deterministic on purpose (sorted names, no timestamps, no counters that change per request), so the prompt cache holds until a file
changes. Directories are collapsed past `depth` to `dir/ (N files)`; a file is one line `path | ~tokens | description`. Over the
character cap the tree is re-rendered one level shallower, and as a last resort cut with a pointer to `kb_tree`.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field

from django_cfg.modules.django_llm.agent.chat.knowledge.base import Entry
from django_cfg.modules.django_llm.agent.chat.knowledge.docs import DESCRIPTION_CHARS, INDEX_NAME, clean_path


@dataclass
class _Node:
    path: str = ""
    files: list[Entry] = field(default_factory=list)
    dirs: dict[str, _Node] = field(default_factory=dict)
    description: str = ""

    def count(self) -> int:
        return len(self.files) + sum(d.count() for d in self.dirs.values())


def _build(entries: Sequence[Entry]) -> _Node:
    root = _Node()
    for e in sorted(entries, key=lambda e: e.path):
        node, parts = root, e.path.split("/")
        for i, part in enumerate(parts[:-1]):
            node = node.dirs.setdefault(part, _Node("/".join(parts[: i + 1])))
        node.files.append(e)
        if parts[-1] == INDEX_NAME:
            node.description = e.description
    return root


def _short(text: str) -> str:
    text = " ".join(text.split())
    return text[: DESCRIPTION_CHARS - 1] + "…" if len(text) > DESCRIPTION_CHARS else text


def _file_line(e: Entry) -> str:
    return f"{e.path} | ~{e.tokens} tok | {_short(e.description)}".rstrip(" |")


def _dir_line(n: _Node) -> str:
    line = f"{n.path}/ ({n.count()} files)"
    return f"{line} — {_short(n.description)}" if n.description else line


def _lines(node: _Node, levels: int, indent: str) -> list[str]:
    out = [indent + _file_line(f) for f in node.files]
    for name in sorted(node.dirs):
        d = node.dirs[name]
        out.append(indent + _dir_line(d))
        if levels > 1:
            out.extend(_lines(d, levels - 1, indent + "  "))
    return out


def render_tree(entries: Sequence[Entry], path: str = "", depth: int = 2, max_chars: int = 6000) -> str:
    """The tree under `path` ("" = root) to `depth` levels (1 = direct children only), within `max_chars`.
    Raises `KeyError` when `path` is not a directory of the tree (the tool turns that into a sentence)."""
    node = _build(entries)
    rel = clean_path(path) if path.strip() else ""
    for part in [p for p in rel.split("/") if p]:
        if part not in node.dirs:
            raise KeyError(rel)
        node = node.dirs[part]
    if not entries:
        return "(the knowledge base is empty)"
    while not rel and not node.files and len(node.dirs) == 1:  # a lone top directory (a scoped base) is the root, not a level
        node = next(iter(node.dirs.values()))
        rel = node.path
    head = [_dir_line(node)] if rel else []
    depth = max(1, min(depth, 6))
    for levels in range(depth, 0, -1):
        body = _lines(node, levels, "  " if rel else "")
        text = "\n".join(head + body)
        if len(text) <= max_chars:
            if levels < depth:
                text += f"\n[deeper levels collapsed to fit; call kb_tree(path, depth={levels + 1}) on a directory to open it]"
            return text
    tail = f"\n[… {{n}} more lines; call kb_tree(path) on a directory]"
    kept: list[str] = []
    used = len(tail) + 8
    for line in head + body:
        if used + len(line) + 1 > max_chars:
            break
        kept.append(line)
        used += len(line) + 1
    return "\n".join(kept) + tail.format(n=len(head + body) - len(kept))
