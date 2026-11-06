"""Text rules of the knowledge base: what is stripped before anything is indexed or shown, and how a query is split into terms.

A file is trusted authorship (it lives in git) but its text is still *data*: HTML comments (a classic hiding place for
instructions) and invisible characters are removed on load, and line numbers are kept (a comment becomes the same number of
empty lines), so a `path:line` citation points at the same line in the editor and in the model's view.
"""

from __future__ import annotations

import math
import re

_COMMENT = re.compile(r"<!--.*?(?:-->|\Z)", re.S)
_INVISIBLE = {c: None for c in (*range(0x200B, 0x2010), *range(0x202A, 0x202F), *range(0x2060, 0x2065), *range(0x2066, 0x206A), 0xFEFF, 0x00AD)}
_CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
WORD = re.compile(r"\w+", re.UNICODE)

#: A query word this common matches everything. English and Russian function words only: change on an eval result.
STOP = frozenset(
    "the and for are can how what when where which who why does with from that this have you your our about much many will there they "
    "not but was were been into than then them its has had any all also use used using get got".split()
    + "как что где когда какой какая какие какое почему зачем можно нужно если или для при это эта этот эти его она они мне вас вам "
    "про над под без все всё так уже ещё еще есть быть был была были будет надо чем там тут ли же бы".split()
)

#: Cyrillic (and any non-ASCII) words are matched by their first letters: Porter stems English only.
PREFIX = 5


def sanitize(text: str) -> tuple[str, int]:
    """`(clean text, how many things were removed)`. Newlines are preserved, so line numbers do not move."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    removed = 0

    def blank(match: re.Match) -> str:
        nonlocal removed
        removed += 1
        return "\n" * match.group(0).count("\n")

    text = _COMMENT.sub(blank, text)
    clean = text.translate(_INVISIBLE)
    removed += len(text) - len(clean)
    final = _CONTROL.sub("", clean)
    removed += len(clean) - len(final)
    return final, removed


def estimate_tokens(text: str) -> int:
    """About four ASCII characters or two others to a token."""
    if not text:
        return 0
    return max(1, math.ceil(sum(0.25 if ord(c) < 128 else 0.5 for c in text)))


_COMPOUND = re.compile(r"\w+(?:-\w+)+")


def terms(query: str) -> list[str]:
    """Distinct lower-case query words without stop words, in order of appearance. A hyphenated compound also adds its joined
    form (`non-profit` -> `nonprofit`, `e-mail` -> `email`): the files spell it either way and the index splits only on the hyphen."""
    low = query.lower()
    seen = dict.fromkeys(w for w in WORD.findall(low) if len(w) > 1 and w not in STOP)
    for m in _COMPOUND.finditer(low):
        seen.setdefault(m.group(0).replace("-", ""), None)
    return list(seen)


def stem(term: str) -> str:
    """The substring a text line must contain to count as a match for `term` (used for snippets, not for the index)."""
    if not term.isascii():
        return term[:PREFIX]
    return term[:-2] if len(term) >= 6 else term


def fts_term(term: str) -> str:
    return f'"{term[:PREFIX]}"*' if not term.isascii() and len(term) > PREFIX else f'"{term}"'
