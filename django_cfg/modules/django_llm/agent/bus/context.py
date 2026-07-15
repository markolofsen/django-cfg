"""Per-run search context — tracks queries, deduplicates results, enforces budgets.

Pure mechanism: it counts searches and tool calls, refuses more once a budget is hit,
and dedups results by ``chunk_id`` so the same passage is not carried twice. Nothing
here names a host. The budgets default to conservative numbers; a host that wants
different limits passes them in (``AgentDeps.get_search_ctx`` does exactly that from
its ``max_*`` fields), which is why the defaults are plain constants and not read from
any host config.
"""

from __future__ import annotations

from dataclasses import dataclass, field

#: Conservative defaults. A host overrides these per-run via the constructor.
DEFAULT_MAX_SEARCHES = 3
DEFAULT_MAX_TOOL_CALLS = 10


@dataclass
class AgentSearchContext:
    searches: list[str] = field(default_factory=list)
    all_results: list = field(default_factory=list)
    chunk_ids_seen: set[str] = field(default_factory=set)
    embedding_calls: int = 0
    tool_calls: int = 0

    max_searches: int = DEFAULT_MAX_SEARCHES
    max_tool_calls: int = DEFAULT_MAX_TOOL_CALLS

    def can_search(self) -> bool:
        return (
            len(self.searches) < self.max_searches
            and self.tool_calls < self.max_tool_calls
        )

    def has_searched(self, query: str) -> bool:
        q = query.lower().strip()
        return any(q == s.lower().strip() for s in self.searches)

    def record_search(self, query: str, results: list) -> None:
        self.searches.append(query)
        self.embedding_calls += 1
        self.tool_calls += 1
        for r in results:
            cid = getattr(r, "chunk_id", None)
            if cid and cid not in self.chunk_ids_seen:
                self.chunk_ids_seen.add(cid)
                self.all_results.append(r)

    def record_tool_call(self) -> None:
        self.tool_calls += 1

    def prior_topics(self) -> list[str]:
        """Top keywords from accumulated result titles — for contextual enrichment."""
        words: dict[str, int] = {}
        for r in self.all_results:
            title = getattr(r, "document_title", "") or ""
            for w in title.split():
                if len(w) > 3:
                    words[w.lower()] = words.get(w.lower(), 0) + 1
        return [w for w, _ in sorted(words.items(), key=lambda x: -x[1])][:8]
