"""The knowledge base itself: values, the `KnowledgeBase` Protocol, and the three backends the tools can sit on.

* `DiskKnowledgeBase(root)` reads a folder; the index is rebuilt when the folder changes (names, sizes and mtimes are looked at most
  every `refresh_s` seconds). A missing folder is an empty base, not an error.
* `StubKnowledgeBase({path: text})` is the same engine over in-memory files, for tests and for hosts that build text themselves.
* `ScopedKnowledgeBase(inner, prefix)` shows one subfolder of another base (paths stay root-relative), the audience-scoping seam.

A host that wants Postgres FTS or pgvector later implements the Protocol and the tools do not change.
"""

from __future__ import annotations

import difflib
import hashlib
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, runtime_checkable

from django_cfg.modules.django_llm.agent.chat.knowledge import docs as docs_mod
from django_cfg.modules.django_llm.agent.chat.knowledge.chunker import Heading, headings
from django_cfg.modules.django_llm.agent.chat.knowledge.index import Hit, Index

MAX_READ_LINES = 200
MAX_READ_CHARS = 12_000
MAX_LINE_CHARS = 1500


class KbError(Exception):
    """Something the model can be told in a sentence (it is returned as tool text, never raised to the run)."""


class KbNotFound(KbError):
    pass


class KbPathError(KbError):
    pass


@dataclass(frozen=True)
class Entry:
    path: str
    title: str
    description: str
    aliases: tuple[str, ...]
    tokens: int
    lines: int
    is_index: bool = False


@dataclass(frozen=True)
class Page:
    path: str
    start: int
    end: int
    total: int
    text: str  # numbered lines: "  12| text"
    capped: bool = False  # the request asked for more than a call may return

    def __str__(self) -> str:
        return self.text

    def find_line(self, needle: str) -> int | None:
        """The absolute line number of the first line of this page containing `needle`, or `None`."""
        for row in self.text.split("\n"):
            number, bar, rest = row.partition("|")
            if bar and needle in rest and number.strip().isdigit():
                return int(number)
        return None

    @property
    def footer(self) -> str:
        if self.end >= self.total:
            return f"[lines {self.start}-{self.end} of {self.total}; end of file]"
        return f"[lines {self.start}-{self.end} of {self.total}; continue with start_line={self.end + 1}]"


@runtime_checkable
class KnowledgeBase(Protocol):
    def version(self) -> str:
        """A short stable id of the content: the prompt prefix carries it, so it must not change unless a file does."""
        ...

    def entries(self) -> list[Entry]:
        """Every file, sorted by path."""
        ...

    def search(self, query: str, *, path_prefix: str = "", limit: int = 8) -> list[Hit]: ...

    def outline(self, path: str) -> list[Heading]: ...

    def read(self, path: str, start_line: int = 1, end_line: int | None = None, *, section: str | None = None) -> Page: ...


@dataclass(frozen=True)
class Snapshot:
    docs: dict[str, docs_mod.Doc]
    skipped: tuple[docs_mod.Skipped, ...]
    index: Index
    entries: tuple[Entry, ...]
    version: str


def build_snapshot(scan: docs_mod.Scan) -> Snapshot:
    docs = sorted(scan.docs, key=lambda d: d.path)
    version = hashlib.sha1("\n".join(f"{d.path}:{d.sha}" for d in docs).encode()).hexdigest()[:10]
    entries = tuple(Entry(d.path, d.title, d.description, d.aliases, d.tokens, len(d.lines), d.is_index) for d in docs)
    return Snapshot({d.path: d for d in docs}, tuple(scan.skipped), Index(docs), entries, version)


class _Engine:
    """The Protocol over a `Snapshot`; subclasses decide where the snapshot comes from."""

    def snapshot(self) -> Snapshot:  # pragma: no cover - abstract
        raise NotImplementedError

    def version(self) -> str:
        return self.snapshot().version

    def entries(self) -> list[Entry]:
        return list(self.snapshot().entries)

    def search(self, query: str, *, path_prefix: str = "", limit: int = 8) -> list[Hit]:
        try:
            prefix = docs_mod.clean_path(path_prefix) if path_prefix.strip() else ""
        except docs_mod.PathRejected as exc:
            raise KbPathError(str(exc)) from None
        return self.snapshot().index.search(query, path_prefix=prefix, limit=max(1, min(int(limit), 15)))

    def _doc(self, path: str) -> docs_mod.Doc:
        snap = self.snapshot()
        try:
            rel = docs_mod.clean_doc_path(path)
        except docs_mod.PathRejected as exc:
            raise KbPathError(str(exc)) from None
        doc = snap.docs.get(rel)
        if doc is None:
            near = difflib.get_close_matches(rel, list(snap.docs), n=3, cutoff=0.5)
            raise KbNotFound(f"no such file: {rel}" + (f". Did you mean: {', '.join(near)}?" if near else ". Use kb_tree or kb_search."))
        return doc

    def outline(self, path: str) -> list[Heading]:
        doc = self._doc(path)
        return headings(doc.lines[doc.body_start - 1 :], doc.body_start)

    def read(self, path: str, start_line: int = 1, end_line: int | None = None, *, section: str | None = None) -> Page:
        doc = self._doc(path)
        total = len(doc.lines)
        if section:
            found = _find_section(self.outline(doc.path), section)
            if found is None:
                raise KbNotFound(f"no heading like {section!r} in {doc.path}; call kb_outline")
            start_line, end_line = found.line, found.end
        start = max(1, int(start_line or 1))
        if start > total:
            raise KbError(f"{doc.path} has {total} lines; start_line={start} is past the end")
        want_end = total if end_line is None else min(total, max(start, int(end_line)))
        if end_line is None:
            want_end = min(total, start + MAX_READ_LINES - 1)
        end = min(want_end, start + MAX_READ_LINES - 1)
        out: list[str] = []
        used = 0
        for n in range(start, end + 1):
            line = doc.lines[n - 1]
            if len(line) > MAX_LINE_CHARS:
                line = line[:MAX_LINE_CHARS] + "…[line cut]"
            row = f"{n:>5}| {line}"
            if out and used + len(row) + 1 > MAX_READ_CHARS:
                end = n - 1
                break
            out.append(row)
            used += len(row) + 1
        return Page(doc.path, start, end, total, "\n".join(out), capped=end < want_end)


def _find_section(outline: list[Heading], wanted: str) -> Heading | None:
    key = " ".join(wanted.lower().lstrip("# ").split())
    for h in outline:
        if h.text.lower() == key:
            return h
    return next((h for h in outline if key and key in h.text.lower()), None)


class DiskKnowledgeBase(_Engine):
    def __init__(self, root: str | Path, *, refresh_s: float = 5.0, max_files: int = docs_mod.MAX_FILES, max_file_bytes: int = docs_mod.MAX_FILE_BYTES):
        self.root = Path(root)
        self.refresh_s, self.max_files, self.max_file_bytes = refresh_s, max_files, max_file_bytes
        self._lock = threading.Lock()
        self._snap: Snapshot | None = None
        self._finger = ""
        self._checked = 0.0

    @property
    def exists(self) -> bool:
        return self.root.is_dir()

    def snapshot(self) -> Snapshot:
        with self._lock:
            now = time.monotonic()
            if self._snap is not None and now - self._checked < self.refresh_s:
                return self._snap
            if not self.root.is_dir():
                self._snap, self._finger, self._checked = build_snapshot(docs_mod.Scan()), "", now
                return self._snap
            finger = docs_mod.fingerprint(self.root, max_files=self.max_files)
            if self._snap is None or finger != self._finger:
                self._snap = build_snapshot(docs_mod.scan(self.root, max_files=self.max_files, max_file_bytes=self.max_file_bytes))
                self._finger = finger
            self._checked = now
            return self._snap

    def refresh(self) -> None:
        """Forget what was checked: the next call looks at the folder again."""
        with self._lock:
            self._checked = 0.0


class StubKnowledgeBase(_Engine):
    def __init__(self, files: dict[str, str]):
        scan = docs_mod.Scan()
        for path, text in files.items():
            scan.docs.append(docs_mod.make_doc(docs_mod.clean_doc_path(path), text))
        self._snap = build_snapshot(scan)

    def snapshot(self) -> Snapshot:
        return self._snap


class ScopedKnowledgeBase:
    """One subfolder of `inner`. Paths stay relative to the inner root. A path outside the scope reads as missing."""

    def __init__(self, inner: KnowledgeBase, prefix: str):
        self.inner = inner
        self.prefix = docs_mod.clean_path(prefix).rstrip("/")

    def _inside(self, path: str) -> bool:
        return path == self.prefix or path.startswith(self.prefix + "/")

    def version(self) -> str:
        return hashlib.sha1(f"{self.inner.version()}|{self.prefix}|" .encode() + "\n".join(f"{e.path}" for e in self.entries()).encode()).hexdigest()[:10]

    def entries(self) -> list[Entry]:
        return [e for e in self.inner.entries() if self._inside(e.path)]

    def search(self, query: str, *, path_prefix: str = "", limit: int = 8) -> list[Hit]:
        wanted = docs_mod.clean_path(path_prefix) if path_prefix.strip() else self.prefix
        if not self._inside(wanted):
            return []
        return self.inner.search(query, path_prefix=wanted, limit=limit)

    def outline(self, path: str) -> list[Heading]:
        self._check(path)
        return self.inner.outline(path)

    def read(self, path: str, start_line: int = 1, end_line: int | None = None, *, section: str | None = None) -> Page:
        self._check(path)
        return self.inner.read(path, start_line, end_line, section=section)

    def _check(self, path: str) -> None:
        try:
            rel = docs_mod.clean_doc_path(path)
        except docs_mod.PathRejected as exc:
            raise KbPathError(str(exc)) from None
        if not self._inside(rel):
            raise KbNotFound(f"no such file: {rel}. Use kb_tree or kb_search.")
