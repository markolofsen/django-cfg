"""Lint a knowledge folder: what `kb_check` reports. Errors fail the command; warnings fail it only with `--strict`."""

from __future__ import annotations

import posixpath
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from django_cfg.modules.django_llm.agent.chat.knowledge.base import Snapshot
from django_cfg.modules.django_llm.agent.chat.knowledge.docs import DESCRIPTION_CHARS
from django_cfg.modules.django_llm.agent.chat.knowledge.tools import Caps
from django_cfg.modules.django_llm.agent.chat.knowledge.tree import render_tree

OVERSIZE_LINES = 5000
OVERSIZE_BYTES = 1_000_000
_LINK = re.compile(r"\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
_FENCE = re.compile(r"^\s*(```|~~~)")


@dataclass(frozen=True)
class Problem:
    level: str  # error | warning | info
    path: str
    code: str
    message: str

    def __str__(self) -> str:
        return f"{self.level.upper():7} {self.path or '-'} [{self.code}] {self.message}"


@dataclass
class Report:
    files: int = 0
    tokens: int = 0
    version: str = ""
    tree_chars: int = 0
    problems: list[Problem] = field(default_factory=list)
    strict: bool = False  # what `ok()` uses when called without an argument
    root: str = ""

    def count(self, level: str) -> int:
        return sum(1 for p in self.problems if p.level == level)

    def ok(self, strict: bool | None = None) -> bool:
        strict = self.strict if strict is None else strict
        return self.count("error") == 0 and not (strict and self.count("warning"))

    def summary(self) -> str:
        """One greppable line, `kb_check: OK|FAILED key=value ...`; the last line `kb_check` prints."""
        return (
            f"kb_check: {'OK' if self.ok() else 'FAILED'} errors={self.count('error')} warnings={self.count('warning')} "
            f"files={self.files} tokens={self.tokens} tree_chars={self.tree_chars} version={self.version} strict={str(self.strict).lower()} root={self.root or '-'}"
        )


def check(snapshot: Snapshot, caps: Caps | None = None) -> Report:
    caps = caps or Caps()
    rep = Report(files=len(snapshot.docs), tokens=sum(d.tokens for d in snapshot.docs.values()), version=snapshot.version)
    add = rep.problems.append
    for s in snapshot.skipped:
        add(Problem("error" if "not UTF-8" in s.reason or "outside" in s.reason else "warning", s.path, "skipped", s.reason))
    titles: dict[str, list[str]] = defaultdict(list)
    for doc in snapshot.docs.values():
        titles[doc.title.lower()].append(doc.path)
        for problem in doc.problems:
            add(Problem("error", doc.path, "front-matter", problem))
        for note in doc.notes:
            add(Problem("warning", doc.path, "front-matter-lenient", note))
        if not doc.has_front_matter:
            add(Problem("warning", doc.path, "no-front-matter", "no front matter: title and description are guessed from the text"))
        elif not doc.has_description:
            add(Problem("warning", doc.path, "no-description", "front matter has no description (say which question the file answers)"))
        if len(doc.description) > DESCRIPTION_CHARS:
            add(Problem("warning", doc.path, "long-description", f"description is {len(doc.description)} characters; the tree shows {DESCRIPTION_CHARS}"))
        if len(doc.lines) > OVERSIZE_LINES or doc.size > OVERSIZE_BYTES:
            add(Problem("warning", doc.path, "oversize", f"{len(doc.lines)} lines, {doc.size} bytes: split it or give it _index.md-sized parts"))
        if not any(line.strip() for line in doc.lines[doc.body_start - 1 :]):
            add(Problem("warning", doc.path, "empty", "no text after the front matter"))
        if doc.stripped:
            add(Problem("info", doc.path, "stripped", f"{doc.stripped} HTML comment(s) / invisible character(s) removed from what the model sees"))
        fenced = False
        for n, line in enumerate(doc.lines, 1):
            if _FENCE.match(line):
                fenced = not fenced
            if fenced:
                continue
            for target in _LINK.findall(line):
                dead = _dead_link(doc.path, target, snapshot)
                if dead:
                    add(Problem("warning", f"{doc.path}:{n}", "dead-link", f"link to {dead} resolves to no file"))
    for title, paths in sorted(titles.items()):
        if len(paths) > 1:
            add(Problem("warning", paths[0], "duplicate-title", f"title {title!r} is also used by {', '.join(paths[1:])}"))
    tree = render_tree(snapshot.entries, "", 2, 10**9)
    rep.tree_chars = len(tree)
    if len(tree) > caps.prefix_tree_chars:
        add(Problem("warning", "", "tree-size", f"the tree is {len(tree)} characters; the prompt cap is {caps.prefix_tree_chars}, so it is shown shallower. Add _index.md descriptions or fewer, larger files"))
    rep.problems.sort(key=lambda p: ({"error": 0, "warning": 1, "info": 2}[p.level], p.path, p.code))
    return rep


def check_dir(path: str | Path, strict: bool = False, caps: Caps | None = None) -> Report:
    """Lint a folder on disk: `check_dir(root, strict=True).ok()` in a host's test. A folder that does not exist is one error."""
    from django_cfg.modules.django_llm.agent.chat.knowledge.base import DiskKnowledgeBase

    root = Path(path).expanduser()
    if not root.is_dir():
        rep = Report(strict=strict, root=str(root))
        rep.problems.append(Problem("error", "", "missing", f"{root} is not a directory"))
        return rep
    rep = check(DiskKnowledgeBase(root, refresh_s=0).snapshot(), caps)
    rep.strict, rep.root = strict, str(root)
    return rep


def _dead_link(source: str, target: str, snap: Snapshot) -> str:
    if re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I) or target.startswith("#"):
        return ""
    clean = target.split("#", 1)[0].split("?", 1)[0]
    if not clean or not clean.lower().endswith((".md", ".mdx", ".txt")):
        return ""
    path = clean.lstrip("/") if clean.startswith("/") else posixpath.normpath(posixpath.join(posixpath.dirname(source), clean))
    return "" if path in snap.docs else path
