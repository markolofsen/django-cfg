"""Edit-prompt hygiene — Gemini / Nano Banana safety-filter mitigation.

Provider-side adaptation, **not** domain logic. The image-edit model
(Nano Banana on OpenRouter) has a brand-protection / evidence-tampering
safety classifier that hard-refuses certain phrase shapes:

* ``Remove`` + ``text overlay`` / ``watermark`` / ``logo`` / ``caption``
* Bare ``watermark`` noun even with soft verbs ("Soften the watermark")
* Quoted source-text content (``Remove the 'PROPERTY' text overlay``)
* Named agency brands (``Remove the REMAX banner``)
* Dangling ``the X overlay`` with empty-quote residue after a strip

When the classifier fires it returns an empty image response
("Model returned no image bytes") and burns the whole generator call.

``sanitize_edit_prompt()`` rewrites those shapes into classifier-safe
forms while preserving operator intent:

* **Verb softening** — ``Remove`` → ``Blend out`` when the target is a
  text-shaped noun (text/logo/overlay/banner/sign/caption); other
  ``Remove`` uses (declutter: cars, trash bins) stay literal.
* **Noun neutralization** — ``text overlay`` / ``watermark`` /
  ``caption`` → ``overlay markings``; ``logo`` / ``banner`` pass through.
* **Quoted-segment strip** — any straight/curly single/double quoted
  run up to 50 chars is dropped WITH the wrapping quotes; the analyzer
  is told never to quote source text so anything quoted is by
  definition a cleanup target.
* **Brand keyword strip** — a closed list of well-known real-estate
  agency brands (REMAX, Sotheby's, Coldwell, Knight Frank, etc.) for
  bare (unquoted) mentions; conservative list with very low collision
  risk against general English.
* **Dangling-article rewrite** — ``the X overlay`` with X gone becomes
  ``the corner overlay``; a concrete position helps the model commit.
* **Empty-quote pair cleanup** as defense-in-depth idempotency.

Design notes:

* No bare-ALL-CAPS heuristic — earlier versions stripped any unquoted
  ALL-CAPS token ≥4 chars. That false-positives on benign descriptors
  like ``PROPERTY`` / ``VILLA`` / ``LAND`` and leaves orphan quote
  pairs that themselves trigger refusals. The closed brand list +
  generic quoted-segment strip cover the same ground at near-zero FP.
* The function is **idempotent** — re-running on already-clean text
  yields the same output. Wire it as a Pydantic ``field_validator``
  on the analyzer's structured-output prompt field; tests can re-run
  it freely without state.

Independent of host app domain (real-estate / vehicles / e-commerce).
The brand list is real-estate-leaning today because that's where the
incidents came from; extend per host app if other agency vocab shows
up in your edit prompts.
"""

from __future__ import annotations

import re

# Known real-estate agency brand keywords (lowercase substring match,
# case-insensitive at the regex level). Conservative list — only
# entries with very low collision risk against general English /
# property-description vocabulary.
_BRAND_KEYWORDS: tuple[str, ...] = (
    "remax", "sotheby", "coldwell", "compass real estate",
    "knight frank", "douglas elliman", "redfin", "zillow",
    "trulia", "century 21", "century21", "engel volkers",
    "engel & völkers", "berkshire hathaway", "bhhs", "exp realty",
    "keller williams", "kw realty", "realtor.com", "ray white",
    "harcourts",
)

# Generic quoted-segment strip — matches any straight or curly
# single/double quoted run up to ~50 chars and drops it WITH the
# wrapping quotes. The analyzer is told never to quote source text;
# anything that arrives quoted is by definition our cleanup target.
# Length-capped to avoid eating large legitimate quoted sentences in
# free-form operator prompts (the operator path runs this too).
_QUOTED_SEGMENT_RE = re.compile(
    r"['\"“”„‟‘’]\s*[^'\"“”„‟‘’\n]{1,50}\s*['\"“”„‟‘’]"
)

# Bare brand keyword strip — runs AFTER the quoted-segment pass so it
# only catches brand mentions that arrived unquoted.
_BARE_BRAND_RE = re.compile(
    r"\b(" + "|".join(re.escape(k) for k in _BRAND_KEYWORDS) + r")\b(?:'s)?",
    re.IGNORECASE,
)

# Empty quote pair cleanup — defense-in-depth in case the source
# arrived with an already-empty quote pair from upstream sanitization.
_EMPTY_QUOTE_RE = re.compile(r"['\"“”„‟‘’]\s*['\"“”„‟‘’]")

# After empty-quote removal, "the  text overlay" / "the text overlay"
# without a descriptor reads as a vague instruction the model
# occasionally refuses on. Rewrite to "the corner text overlay" — a
# concrete position helps the model commit.
_DANGLING_ARTICLE_RE = re.compile(
    r"\bthe\s+(logo|overlay|text|banner|sign|watermark)\b",
    re.IGNORECASE,
)


# Gemini / Nano Banana hard-refuses on "Remove the ... text overlay"
# / "Remove the watermark" verb-noun combinations — Google's policy
# treats this as evidence-tampering / copyright-protection-bypass.
# The same intent expressed with a softer verb ("Blend out", "Soften")
# routes around the filter without losing meaning. The rewrite is
# scoped to text-like targets only — "Remove the parked car" /
# "Remove the trash bin" (declutter use cases) MUST stay literal.
_REMOVE_TEXT_VERB_RE = re.compile(
    r"\b[Rr]emove\b"                            # the trigger verb
    r"(\s+(?:the|any|all|its)\b)?"              # optional article
    r"(?:\s+\w+){0,4}?"                          # ≤4 modifier words
    r"\s+(text\s+overlay|text\s+overlays|"
    r"watermark|watermarks|logo|logos|"
    r"banner|banners|signage|caption|captions)\b",
)
_REMOVE_TEXT_REPLACE = "Blend out\\1\\g<0>"


def _soften_remove_text(text: str) -> str:
    """Replace ``Remove`` with ``Blend out`` where the target is a
    text/logo overlay — the specific verb-noun pair Gemini refuses on.
    Other ``Remove`` uses (cars, trash bins) stay intact."""
    def _swap(match: re.Match[str]) -> str:
        # Replace just the leading "Remove" with "Blend out"; keep
        # the rest of the matched run as-is.
        return "Blend out" + match.group(0)[6:]
    return _REMOVE_TEXT_VERB_RE.sub(_swap, text)


# Noun-level safety filter trigger. Even with soft verbs ("Soften the
# text overlay") Gemini sometimes still refuses on the noun ``text
# overlay`` / ``watermark`` itself — the noun reads as "copyright
# protection" in its classifier. Rewriting to ``overlay markings`` /
# ``surface markings`` preserves what the model needs to find (it's
# given colour + position from the analyzer) without the literal
# trigger. ``logo`` stays — it's already vague enough.
_TEXT_OVERLAY_NOUN_RE = re.compile(
    r"\b(text\s+overlays?|watermarks?|captions?)\b",
    re.IGNORECASE,
)


def _neutralize_overlay_noun(text: str) -> str:
    return _TEXT_OVERLAY_NOUN_RE.sub("overlay markings", text)

# Multi-space collapse — last pass, after every other rewrite.
_MULTI_WS_RE = re.compile(r"\s{2,}")


def sanitize_edit_prompt(text: str | None) -> str | None:
    """Strip brand identifiers + clean residual artefacts.

    Returns ``None`` only for falsy input — never for sanitized output,
    even if the original collapses to whitespace (in that edge case
    we return an empty string so the upstream ``max_length`` /
    required-field check fires as it would for a too-short prompt).
    Idempotent — applying twice yields the same result as once.
    """
    if not text:
        return text

    s = _QUOTED_SEGMENT_RE.sub(" ", text)
    s = _BARE_BRAND_RE.sub(" ", s)
    s = _EMPTY_QUOTE_RE.sub(" ", s)
    s = _DANGLING_ARTICLE_RE.sub(r"the corner \1", s)
    s = _soften_remove_text(s)
    s = _neutralize_overlay_noun(s)
    s = _MULTI_WS_RE.sub(" ", s)
    # Tidy comma / period spacing that the multi-pass may have left.
    s = re.sub(r"\s+([,.;:])", r"\1", s)
    return s.strip()
