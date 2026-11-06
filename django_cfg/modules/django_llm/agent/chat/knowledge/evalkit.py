"""Does a question reach the file that answers it? The eval behind the "do we need embeddings" decision (plan K4).

Adapted from Carapis `crm/knowledge/retrieval.py`. A case is `{"q": ..., "lang": "ru", "query": "<English search terms>", "gold": ["a/b.md"]}`;
a gold path may be a list (any of them counts). Two modes, same report:

* `run_index(kb, cases)`: `kb.search(case["query"])`, deterministic, no model, runs in CI. `query` is what a good model would search
  for after translating the question, written once in the fixture.
* `run_agent(kind, cases, model)`: the question goes through the real loop with a real model; the ranked list is the files the model
  surfaced (kb_search hits in order, then files it opened), so recall@8 asks "did the answer's evidence include the gold file".

A gold path that is not in the base **fails the run** (`Report.missing`), never skips: a skipped case shrinks the denominator silently.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from django_cfg.modules.django_llm.agent.chat.knowledge.base import KnowledgeBase

K = 8
HIT_LINE = re.compile(r"^([\w./-]+\.(?:md|mdx|txt)):\d+-\d+ \|", re.M)


def load_cases(path: str | Path) -> list[dict]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def gold_of(case: dict) -> set[str]:
    g = case["gold"]
    return {g} if isinstance(g, str) else set(g)


@dataclass
class Tally:
    cases: int = 0
    hits: int = 0
    rr: float = 0.0

    @property
    def recall(self) -> float:
        return self.hits / max(self.cases, 1)

    @property
    def mrr(self) -> float:
        return self.rr / max(self.cases, 1)


@dataclass
class Report:
    mode: str
    k: int = K
    total: Tally = field(default_factory=Tally)
    by_lang: dict[str, Tally] = field(default_factory=lambda: defaultdict(Tally))
    missing: list[str] = field(default_factory=list)  # gold paths the base does not have
    misses: list[dict] = field(default_factory=list)  # {"q", "lang", "gold", "got"}
    errors: list[str] = field(default_factory=list)  # agent mode: a run that failed counts as a miss and is listed

    @property
    def ok(self) -> bool:
        return not self.missing

    def add(self, case: dict, ranked: list[str]) -> None:
        gold = gold_of(case)
        top = ranked[: self.k]
        hit = bool(gold & set(top))
        rr = next((1 / (i + 1) for i, p in enumerate(ranked) if p in gold), 0.0)
        for t in (self.total, self.by_lang[case.get("lang", "?")]):
            t.cases += 1
            t.hits += hit
            t.rr += rr
        if not hit:
            self.misses.append({"q": case["q"], "lang": case.get("lang", "?"), "gold": sorted(gold), "got": ranked[:3]})

    def lines(self) -> list[str]:
        out = [f"[{self.mode}] cases {self.total.cases}  recall@{self.k} {self.total.hits}/{self.total.cases} = {self.total.recall:.0%}  MRR {self.total.mrr:.2f}"]
        for lang in sorted(self.by_lang):
            t = self.by_lang[lang]
            out.append(f"  {lang}: recall@{self.k} {t.hits}/{t.cases} = {t.recall:.0%}  MRR {t.mrr:.2f}")
        out += [f"gold not in the base: {g}" for g in self.missing]
        out += [f"miss [{m['lang']}] {m['q']!r}: wanted {m['gold']}, got {m['got']}" for m in self.misses]
        out += [f"error: {e}" for e in self.errors]
        return out


def check_gold(kb: KnowledgeBase, cases: list[dict]) -> list[str]:
    have = {e.path for e in kb.entries()}
    lost: list[str] = []
    for c in cases:
        lost += [g for g in sorted(gold_of(c) - have) if g not in lost]
    return lost


def run_index(kb: KnowledgeBase, cases: list[dict], *, k: int = K) -> Report:
    """Index-only: search with the case's English `query`. A case whose gold is missing from the base is not scored; the run fails."""
    rep = Report("index", k)
    rep.missing = check_gold(kb, cases)
    lost = set(rep.missing)
    for c in cases:
        if not (gold_of(c) - lost):
            continue
        ranked = _unique(h.path for h in kb.search(c["query"], limit=15))
        rep.add(c, ranked)
    return rep


def ranked_paths(tool_calls: list[dict]) -> list[str]:
    """Files an answer surfaced, in order: kb_search hits as printed, then files opened with kb_read / kb_outline."""
    seen: list[str] = []
    for call in tool_calls:
        if call["name"] == "kb_search":
            seen += HIT_LINE.findall(call.get("output") or "")
    for call in tool_calls:
        if call["name"] in ("kb_read", "kb_outline") and (call.get("input") or {}).get("path"):
            seen.append(str(call["input"]["path"]).strip("/"))
    return _unique(seen)


def openrouter_model(name: str, api_key: str) -> Any:
    from pydantic_ai.models.openrouter import OpenRouterModel
    from pydantic_ai.providers.openrouter import OpenRouterProvider

    return OpenRouterModel(name, provider=OpenRouterProvider(api_key=api_key))


async def run_agent(kind: Any, cases: list[dict], model: Any, *, deps: Any = None, k: int = K) -> Report:
    """Agent mode: each question is one fresh answer through `kind_source` (the kind must have `knowledge=` set)."""
    from django_cfg.modules.django_llm.agent.chat.runner import kind_source
    from django_cfg.modules.django_llm.agent.chat.testing import free_pricer
    from django_cfg.modules.django_llm.agent.runtime.streaming import StreamRunResult

    rep = Report("agent", k)
    for c in cases:
        out = StreamRunResult()
        err = ""
        async for ev in kind_source(kind, deps, [], c["q"], model=model, out=out, pricer=free_pricer):
            if ev.type == "error":
                err = str(getattr(ev, "message", "") or getattr(ev, "code", "error"))
        if err:
            rep.errors.append(f"{c['q']!r}: {err}")
        rep.add(c, ranked_paths(out.tool_calls))
    return rep


def _unique(items) -> list[str]:
    seen: dict[str, None] = {}
    for p in items:
        seen.setdefault(p, None)
    return list(seen)
