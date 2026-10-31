"""
The allowlist: what the outbox is allowed to delete.

A deletion is refused, never guessed at, when its key is empty, escapes the
storage root, or sits outside the configured prefixes.
"""

from __future__ import annotations

from typing import Iterable, List, Optional


def normalize_prefixes(prefixes: Iterable[str]) -> List[str]:
    """`"films"` and `"/films/"` both become `"films/"`; blanks are dropped."""
    out: List[str] = []
    for prefix in prefixes:
        cleaned = str(prefix).strip().lstrip("/")
        if cleaned:
            out.append(cleaned if cleaned.endswith("/") else f"{cleaned}/")
    return out


def refusal(key: str, is_prefix: bool, allowed_prefixes: Iterable[str]) -> Optional[str]:
    """The reason a key or prefix must not be deleted, or `None` when it may."""
    if not key or not key.strip():
        return "empty key"
    if "\x00" in key:
        return "key contains a NUL byte"
    if key.startswith("/"):
        return "key starts with '/'"
    if any(part in ("..", ".") for part in key.split("/")):
        return "key has a '.' or '..' segment"
    if is_prefix and not key.endswith("/"):
        return "a prefix must end with '/'"

    allowed = normalize_prefixes(allowed_prefixes)
    if not allowed:
        return "prefix deletion needs allowed_prefixes" if is_prefix else None

    for root in allowed:
        if key.startswith(root) and len(key) > len(root):
            return None
    return f"outside allowed_prefixes ({', '.join(allowed)})"
