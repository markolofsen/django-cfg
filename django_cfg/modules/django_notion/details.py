"""The Details text: every field without a column, one "Label: value" line each.

Rules (same as the Hub "Any field the form sends" page): fixed order (Project key, Company, Source page, Locale, then the rest
alphabetically); nested values flat ("Budget / Min: 10"); lists "a, b"; bool Yes/No; empty values left out; a value over
1000 characters is cut with a note; Details over about 6000 characters ends with the number of fields not shown; honeypot,
timing, idempotency and secret-looking fields are never copied.
"""

from __future__ import annotations

import re
from datetime import date, datetime
from typing import Any, Dict, List, Tuple

MAX_VALUE = 1000
MAX_DETAILS = 6000
PROJECT_KEY_LABEL = "Project key"
FIRST_LABELS = (PROJECT_KEY_LABEL, "Company", "Source page", "Locale")

_EXACT_SKIP = {"website", "startedat", "elapsedms"}
_SKIP_PARTS = (
    "password", "passwd", "token", "apikey", "authorization", "captcha", "turnstile", "cookie", "secret",
    "csrf", "idempotency",
)


def is_forbidden(name: str) -> bool:
    """True for honeypot/timing fields, idempotency or Hub keys and anything whose name says it is a secret."""
    flat = re.sub(r"[^a-z0-9]", "", str(name).lower())
    if flat in _EXACT_SKIP or flat.startswith("hub"):
        return True
    return any(part in flat for part in _SKIP_PARTS)


def humanize(name: str) -> str:
    """``sourcePage`` / ``source_page`` -> ``Source page``."""
    s = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", str(name))
    s = re.sub(r"[_\-\s]+", " ", s).strip().lower()
    return s[:1].upper() + s[1:]


def _scalar(value: Any) -> str:
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return str(value).strip()


def _flatten(label: str, value: Any, out: List[Tuple[str, str]]) -> None:
    if value is None:
        return
    if isinstance(value, dict):
        for k, v in value.items():
            if is_forbidden(k):
                continue
            _flatten(f"{label} / {humanize(k)}", v, out)
        return
    if isinstance(value, (list, tuple, set)):
        items = list(value)
        if all(not isinstance(i, (dict, list, tuple, set)) for i in items):
            text = ", ".join(t for t in (_scalar(i) for i in items if i is not None) if t)
            if text:
                out.append((label, text))
        else:
            for n, item in enumerate(items, 1):
                _flatten(f"{label} / {n}", item, out)
        return
    text = _scalar(value)
    if text:
        out.append((label, text))


def _cut(text: str) -> str:
    if len(text) <= MAX_VALUE:
        return text
    return f"{text[:MAX_VALUE]}… [{len(text) - MAX_VALUE} characters not shown]"


def build_details(extra: Dict[str, Any]) -> str:
    """Return the Details text for ``extra`` ("" when nothing is left)."""
    pairs: List[Tuple[str, str]] = []
    for key, value in (extra or {}).items():
        if is_forbidden(key):
            continue
        _flatten(humanize(key), value, pairs)

    def order(pair: Tuple[str, str]):
        head = pair[0].split(" / ")[0]
        return (FIRST_LABELS.index(head), "") if head in FIRST_LABELS else (len(FIRST_LABELS), pair[0].lower())

    pairs.sort(key=order)
    lines: List[str] = []
    used = 0
    for i, (label, value) in enumerate(pairs):
        line = f"{label}: {_cut(value)}"
        if used + len(line) + 1 > MAX_DETAILS and lines:
            lines.append(f"… {len(pairs) - i} more fields not shown")
            break
        lines.append(line)
        used += len(line) + 1
    return "\n".join(lines)
