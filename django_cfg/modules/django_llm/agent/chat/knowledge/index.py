"""The in-process search index: SQLite FTS5 in memory, built from `Doc`s, one per worker.

Columns and weights (bm25): title 10, aliases 12 (synonyms and other-language keywords, the top weight), summary 3 (description and
path words), heading 4, body 1. Title, aliases and summary repeat on every chunk of a file, so the best *chunk* of a matching file
wins on its body. A query is `OR` of its terms; Porter stems English; a non-ASCII word matches by its first letters (the Carapis fix:
`unicode61` does not stem Cyrillic). At most `PER_DOC` chunks of one file are returned, so a large file cannot fill the list.
"""

from __future__ import annotations

import sqlite3
import threading
from collections.abc import Sequence
from dataclasses import dataclass

from django_cfg.modules.django_llm.agent.chat.knowledge import chunker
from django_cfg.modules.django_llm.agent.chat.knowledge.docs import Doc
from django_cfg.modules.django_llm.agent.chat.knowledge.text import fts_term, stem, terms

PER_DOC = 2
WEIGHTS = (10.0, 12.0, 3.0, 4.0, 1.0)
SNIPPET_CHARS = 160


@dataclass(frozen=True)
class Hit:
    path: str
    start: int
    end: int
    crumb: str  # "Setup > Install"
    snippet: str
    snippet_line: int
    title: str = ""


class Index:
    def __init__(self, docs: Sequence[Doc]):
        self._lock = threading.Lock()
        self._docs = {d.path: d for d in docs}
        self._db = sqlite3.connect(":memory:", check_same_thread=False)
        self._db.execute("create table chunks(id integer primary key, path text, start integer, end integer, crumb text)")
        self._db.execute("create index chunks_path on chunks(path)")
        self._db.execute("create virtual table fts using fts5(title, aliases, summary, heading, body, tokenize='porter unicode61')")
        rows_c, rows_f, n = [], [], 0
        for doc in docs:
            pieces = chunker.chunk(doc.lines[doc.body_start - 1 :], doc.body_start) or [
                chunker.Chunk(1, max(1, len(doc.lines)), (), doc.title)
            ]
            summary = f"{doc.description} {doc.path.replace('/', ' ').replace('_', ' ').replace('-', ' ')}"
            for p in pieces:
                n += 1
                crumb = " > ".join(p.crumb)
                rows_c.append((n, doc.path, p.start, p.end, crumb))
                rows_f.append((n, doc.title, " ; ".join(doc.aliases), summary, crumb, p.text))
        self._db.executemany("insert into chunks values (?,?,?,?,?)", rows_c)
        self._db.executemany("insert into fts(rowid, title, aliases, summary, heading, body) values (?,?,?,?,?,?)", rows_f)
        self.chunks = n

    def search(self, query: str, *, path_prefix: str = "", limit: int = 8) -> list[Hit]:
        words = terms(query)
        if not words:
            return []
        match = " OR ".join(fts_term(w) for w in words)
        prefix = path_prefix.strip("/")
        guard, args = "", []
        if prefix:
            guard = "and (c.path = ? or substr(c.path, 1, ?) = ?)"
            args = [prefix, len(prefix) + 1, prefix + "/"]
        sql = (
            "select c.path, c.start, c.end, c.crumb from fts join chunks c on c.id = fts.rowid "
            f"where fts match ? {guard} order by bm25(fts, {', '.join(map(str, WEIGHTS))}), c.path, c.start limit ?"
        )
        with self._lock:
            try:
                rows = self._db.execute(sql, [match, *args, max(limit, 1) * 6]).fetchall()
            except sqlite3.OperationalError:
                return []
        per: dict[str, int] = {}
        hits: list[Hit] = []
        for path, start, end, crumb in rows:
            if per.get(path, 0) >= PER_DOC:
                continue
            per[path] = per.get(path, 0) + 1
            doc = self._docs[path]
            line, snippet = _snippet(doc, start, end, words)
            hits.append(Hit(path, start, end, crumb, snippet, line, doc.title))
            if len(hits) >= limit:
                break
        return hits


def _snippet(doc: Doc, start: int, end: int, words: list[str]) -> tuple[int, str]:
    needles = [stem(w) for w in words]
    best, best_score = start, -1
    for n in range(start, min(end, len(doc.lines)) + 1):
        low = doc.lines[n - 1].lower()
        if not low.strip():
            continue
        score = sum(1 for s in needles if s in low)
        if score > best_score:
            best, best_score = n, score
    text = " ".join(doc.lines[best - 1].split()) if best <= len(doc.lines) else ""
    return best, (text[: SNIPPET_CHARS - 1] + "…") if len(text) > SNIPPET_CHARS else text
