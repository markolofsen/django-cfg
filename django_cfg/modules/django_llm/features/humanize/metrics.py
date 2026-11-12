"""Local, deterministic scoring of how machine-written a text reads (0 human .. 100 machine).

No model call and no external detector: a score is only a *steering signal* for
the rewrite loop (what to cut, when to stop). It does not predict any vendor's
detector and nothing here claims a text "passes" one.

Signals (each capped, summed):
  tells        phrases from ``lexicon.py``, per 100 words            max 40
  burstiness   sentence-length variation; machines write evenly      max 25
  openers      sentences starting on the same word                   max 12
  dashes       em-dash / emoji density                               max 10
  paragraphs   uniform paragraph length (3+ paragraphs)              max 8
  tricolon     "A, B and C" triples in many sentences                max 5
"""

from __future__ import annotations

import re
import statistics
from dataclasses import dataclass, field

from .lexicon import EMOJI_RE, LEXICON, OPENER_STOP

_SENT_SPLIT = re.compile(r"(?<=[.!?…])\s+(?=[\"'«(\[]?[\w])", re.UNICODE)
_WORD = re.compile(r"[\w'’-]+", re.UNICODE)
_TRICOLON = re.compile(r"\b[\w-]+, [\w-]+,? (?:and|и|или|or) [\w-]+\b", re.UNICODE)
_CYR = re.compile(r"[а-яё]", re.IGNORECASE)


@dataclass(frozen=True)
class Finding:
    kind: str          # tell | rhythm | opener | dash | structure
    text: str          # the offending phrase / description
    hint: str


@dataclass(frozen=True)
class Report:
    score: float
    lang: str
    words: int
    findings: tuple[Finding, ...] = field(default_factory=tuple)
    stats: dict = field(default_factory=dict)


def detect_lang(text: str) -> str:
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return "en"
    cyr = sum(1 for c in letters if _CYR.match(c))
    return "ru" if cyr / len(letters) > 0.4 else "en"


def sentences(text: str) -> list[str]:
    out: list[str] = []
    for para in re.split(r"\n\s*\n|\n(?=[-*•#\d])", text):
        para = para.strip()
        if para:
            out.extend(s.strip() for s in _SENT_SPLIT.split(para) if s.strip())
    return out


def _cv(values: list[float]) -> float:
    if len(values) < 2:
        return 1.0
    mean = statistics.fmean(values)
    return statistics.pstdev(values) / mean if mean else 0.0


def analyze(text: str, lang: str | None = None) -> Report:
    lang = lang or detect_lang(text)
    words = _WORD.findall(text)
    n_words = len(words)
    if n_words == 0:
        return Report(0.0, lang, 0)

    findings: list[Finding] = []
    per100 = 100.0 / max(n_words, 40)

    # tells
    weight_sum = 0
    for pattern, weight, hint in LEXICON.get(lang, ()):
        for m in pattern.finditer(text):
            weight_sum += weight
            findings.append(Finding("tell", m.group(0).strip(), hint))
    tells = min(40.0, weight_sum * per100 * 6)

    sents = sentences(text)
    lens = [len(_WORD.findall(s)) for s in sents]
    burst = openers = para = tri = 0.0

    if len(sents) >= 4:
        cv = _cv([float(x) for x in lens])
        burst = max(0.0, min(25.0, (0.55 - cv) / 0.55 * 25))
        if cv < 0.35:
            findings.append(Finding("rhythm", f"sentence lengths too even (cv={cv:.2f})",
                                    "mix short (3-7 words) and long sentences; allow a fragment"))
        firsts = [(_WORD.findall(s) or [""])[0].lower() for s in sents]
        firsts = [f for f in firsts if f and f not in OPENER_STOP]
        if firsts:
            top = max(set(firsts), key=firsts.count)
            share = firsts.count(top) / len(sents)
            openers = min(12.0, max(0.0, share - 0.2) * 40)
            if share > 0.3 and firsts.count(top) >= 3:
                findings.append(Finding("opener", f"{firsts.count(top)} sentences start with '{top}'",
                                        "vary how sentences begin"))
        tri_share = sum(1 for s in sents if _TRICOLON.search(s)) / len(sents)
        tri = min(5.0, tri_share * 20)
        if tri_share > 0.25:
            findings.append(Finding("structure", "many 'A, B and C' lists",
                                    "use two items, or one, where the text does not need three"))

    dashes = text.count("—") + text.count(" – ") + len(EMOJI_RE.findall(text))
    dash = min(10.0, dashes * per100 * 4)
    if dashes >= 2 and dash >= 4:
        findings.append(Finding("dash", f"{dashes} em dashes / emoji", "use periods, commas or colons"))

    paras = [len(_WORD.findall(p)) for p in re.split(r"\n\s*\n", text) if p.strip()]
    if len(paras) >= 3:
        pcv = _cv([float(x) for x in paras])
        para = max(0.0, min(8.0, (0.4 - pcv) / 0.4 * 8))
        if pcv < 0.2:
            findings.append(Finding("structure", "paragraphs all the same size", "let one be a single line"))

    score = round(min(100.0, tells + burst + openers + dash + para + tri), 1)
    stats = {"tells": round(tells, 1), "burstiness": round(burst, 1), "openers": round(openers, 1),
             "dashes": round(dash, 1), "paragraphs": round(para, 1), "tricolon": round(tri, 1),
             "sentences": len(sents)}
    return Report(score, lang, n_words, tuple(findings), stats)
