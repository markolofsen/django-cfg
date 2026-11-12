"""Rewrite loop: score -> name the tells -> rewrite -> verify facts -> score again.

Three ideas, none of them "tell the model to sound human" (that returns the same
machine voice in a new coat):

1. The rewrite prompt carries *this text's* findings (the exact phrases, the flat
   rhythm), so the editor is told what to cut.
2. A rewrite is accepted only if every number, URL, e-mail, `code` and @handle of
   the source survives (``guard.py``) and the length stays in bounds. A rewrite
   that fails is retried with the violation named; if none passes, the SOURCE comes
   back unchanged (``ok=False``) - an unfaithful text is worse than a stiff one.
3. The loop stops when the local score is at or under ``target`` or rounds run out;
   the best faithful candidate wins, never merely the last.

Typos, homoglyphs and zero-width characters are deliberately NOT injected: they
damage the text and search engines read them as spam.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Literal, Sequence

from .guard import extract_facts, length_ok, missing
from .metrics import Finding, Report, analyze, detect_lang

Strength = Literal["light", "medium", "heavy"]

# ask(messages, system, max_tokens, models) -> object with .value (str), .model, .usage
Ask = Callable[[list[dict], str, int | None, Sequence[str] | None], Any]

_STRENGTH: dict[str, str] = {
    "light": "Edit minimally: fix only the listed problems and leave every other sentence as it is.",
    "medium": "Rewrite sentence by sentence where needed; keep the order of points and the paragraphing.",
    "heavy": "Rewrite freely: change sentence structure, merge or split sentences; keep the points and their order.",
}

_LANG_RULES: dict[str, str] = {
    "ru": ("Пиши живым русским языком: без канцелярита, без отглагольных существительных "
           "(«осуществление», «проведение»), глаголы вместо оборотов с «является». "
           "Не калькируй английские конструкции."),
    "en": "Plain, concrete words. Prefer the short verb to the long one.",
}

_SYSTEM = """You are a copy editor. Rewrite the user's text so it reads like something a specific person wrote, \
not like generated prose. Same language as the input.

Hard rules:
- Keep every fact: every number, date, name, URL, e-mail, @handle and `code` span must appear exactly as in the source. Invent nothing, drop nothing.
- Keep the meaning and the point of view. Length: about the same; shorter is fine only where you cut filler, never where you cut information.
- Keep the markup the source uses (headings, lists, links). Add none that is not there.
- No opener that announces the topic and no closing recap or call to action that the source does not already have.
- No rhetorical contrast ("not just X, but Y"), no "whether you are A or B", no stock phrases.
- Do not use em dashes; use a period, comma or colon.
- Sentence length must vary: some very short, some long. Not every sentence has the same shape.
- {strength}
- {lang_rule}
{voice}{domain}
Output ONLY the rewritten text, nothing else."""


@dataclass(frozen=True)
class HumanizeResult:
    text: str                       # the rewrite, or the source when nothing faithful was produced
    ok: bool                        # True: faithful rewrite accepted, or source already clean
    changed: bool
    before: Report
    after: Report
    rounds: int
    reason: str = ""
    models: tuple[str, ...] = ()
    cost_usd: float = 0.0
    history: tuple[float, ...] = field(default_factory=tuple)   # score after each round


def _build_system(lang: str, strength: str, voice: str | None, domain: str | None) -> str:
    return _SYSTEM.format(
        strength=_STRENGTH[strength],
        lang_rule=_LANG_RULES.get(lang, _LANG_RULES["en"]),
        voice=f"- Voice: {voice}\n" if voice else "",
        domain=f"- The text is about: {domain}. Use that field's ordinary terminology.\n" if domain else "",
    )


def _brief(findings: Sequence[Finding], limit: int = 14) -> str:
    seen, lines = set(), []
    for f in findings:
        key = (f.kind, f.text.lower())
        if key in seen:
            continue
        seen.add(key)
        lines.append(f"- [{f.kind}] {f.text!r}: {f.hint}")
        if len(lines) >= limit:
            break
    return "\n".join(lines) or "- (no specific phrase; make the rhythm and word choice less uniform)"


def humanize(
    text: str,
    ask: Ask,
    *,
    lang: str | None = None,
    voice: str | None = None,
    domain: str | None = None,
    strength: Strength = "medium",
    rounds: int = 2,
    target: float = 25.0,
    keep: Sequence[str] = (),
    force: bool = False,
    max_tokens: int | None = None,
    models: Sequence[str] | None = None,
) -> HumanizeResult:
    """Rewrite ``text``; see the module docstring. ``ask`` is the model transport (``tasks`` passes its own)."""
    if strength not in _STRENGTH:
        raise ValueError(f"strength must be one of {sorted(_STRENGTH)}")
    lang = lang or detect_lang(text)
    before = analyze(text, lang)
    if not text.strip():
        return HumanizeResult(text, True, False, before, before, 0, "empty")
    if before.score <= target and not force:
        return HumanizeResult(text, True, False, before, before, 0, "already under target")

    facts = extract_facts(text, tuple(keep))
    system = _build_system(lang, strength, voice, domain)
    best_text, best_report = None, None
    used: list[str] = []
    cost = 0.0
    history: list[float] = []
    feedback = ""
    current_findings = before.findings
    reason = "no faithful rewrite"

    for n in range(1, max(1, rounds) + 1):
        base = best_text if best_text is not None else text
        user = (
            f"Problems found in this text:\n{_brief(current_findings)}\n"
            f"{feedback}\nText to rewrite:\n\n{base}"
        )
        res = ask([{"role": "user", "content": user}], system, max_tokens, models)
        out = (res.value or "").strip()
        used.append(res.model)
        cost += float((res.usage or {}).get("cost_usd") or 0.0)

        lost = missing(facts, out)
        if lost:
            feedback = f"\nYour previous attempt dropped these facts, put them back exactly: {', '.join(lost[:12])}\n"
            reason = f"dropped facts: {', '.join(lost[:5])}"
            history.append(-1.0)
            continue
        if not length_ok(text, out):
            feedback = "\nYour previous attempt changed the length too much; stay close to the source length without cutting information.\n"
            reason = "length out of bounds"
            history.append(-1.0)
            continue

        feedback = ""
        report = analyze(out, lang)
        history.append(report.score)
        current_findings = report.findings
        if best_report is None or report.score < best_report.score:
            best_text, best_report = out, report
        if best_report.score <= target:
            break

    if best_text is None or best_report is None or best_text == text:
        return HumanizeResult(text, False, False, before, before, len(history), reason,
                              tuple(dict.fromkeys(used)), cost, tuple(history))
    if best_report.score > before.score:
        return HumanizeResult(text, False, False, before, before, len(history), "rewrite scored worse",
                              tuple(dict.fromkeys(used)), cost, tuple(history))
    return HumanizeResult(best_text, True, True, before, best_report, len(history), "",
                          tuple(dict.fromkeys(used)), cost, tuple(history))
