"""Realtime topic patterns as the generator reads them (``orders:{order_id:int}``).

The one copy of the pattern grammar on this side; django_realtime owns the declaration side and the generator may
not import it. Imported lazily by ``realtime/generator.py`` and ``hooks/realtime_tags.py`` (import budget).
"""

from __future__ import annotations

import re

#: A colon outside ``{...}``: ``{order_id:int}`` stays one segment.
SPLIT_RE = re.compile(r":(?![^{]*\})")
#: One parameter segment: ``{name}`` or ``{name:str|int}``.
PARAM_RE = re.compile(r"^\{([a-z_][a-z0-9_]*)(?::(str|int))?\}$")


def split_pattern(pattern: str) -> tuple[str, list[tuple[str, str | None]]]:
    """``(base, [(literal, None) | (param_name, kind)])``."""
    parts = SPLIT_RE.split(pattern)
    segments: list[tuple[str, str | None]] = []
    for raw in parts[1:]:
        match = PARAM_RE.match(raw)
        segments.append((match.group(1), match.group(2) or "str") if match else (raw, None))
    return parts[0], segments


__all__ = ["PARAM_RE", "SPLIT_RE", "split_pattern"]
