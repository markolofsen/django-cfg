"""What a rewrite must not lose. Facts are extracted from the source and looked up in the output."""

from __future__ import annotations

import re
from dataclasses import dataclass

_URL = re.compile(r"https?://[^\s)>\]]+|www\.[^\s)>\]]+")
_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_CODE = re.compile(r"`[^`\n]+`")
_HANDLE = re.compile(r"(?<!\w)[@#][\w-]{2,}")
_NUMBER = re.compile(r"\d[\d\s.,:/%-]*\d|\d")


def _norm_number(raw: str) -> str:
    return re.sub(r"[\s]", "", raw).rstrip(".,:-/")


@dataclass(frozen=True)
class Facts:
    tokens: tuple[str, ...]


def extract_facts(text: str, keep: tuple[str, ...] = ()) -> Facts:
    """URLs, e-mails, `code`, @handles/#tags, every number, plus caller-named ``keep`` strings."""
    found: list[str] = []
    rest = text
    for rx in (_URL, _EMAIL, _CODE, _HANDLE):
        found += [m.group(0) for m in rx.finditer(rest)]
        rest = rx.sub(" ", rest)
    found += [_norm_number(m.group(0)) for m in _NUMBER.finditer(rest)]
    found += [k for k in keep if k]
    return Facts(tuple(dict.fromkeys(t for t in found if t)))


def missing(facts: Facts, output: str) -> list[str]:
    """Facts absent from ``output``. Numbers compare with whitespace removed (12 500 == 12500)."""
    squeezed = re.sub(r"\s", "", output)
    out = []
    for token in facts.tokens:
        if token in output or token in squeezed:
            continue
        out.append(token)
    return out


def length_ok(source: str, output: str, lo: float = 0.45, hi: float = 1.5) -> bool:
    if not source.strip():
        return True
    ratio = len(output) / max(len(source), 1)
    return lo <= ratio <= hi
