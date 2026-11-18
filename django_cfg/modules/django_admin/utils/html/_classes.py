"""
The one map from our semantic tones and sizes to the ``cfg-*`` classes.

Every HTML emitter in ``modules/django_admin`` reads these helpers; ``cfg.css``
(``static/django_admin/css/cfg.css``) styles the names. The contract is in
``@dev/active/modern-django/cfg-classes.md``. No Tailwind class is emitted.
"""

from __future__ import annotations

from typing import Any

#: Canonical tones. Inputs outside this set are mapped by ``tone()``.
TONES = ("success", "warning", "danger", "info", "primary", "neutral")

_TONE_ALIASES = {
    "secondary": "neutral",
    "default": "neutral",
    "gray": "neutral",
    "grey": "neutral",
    "base": "neutral",
    "error": "danger",
    "red": "danger",
    "green": "success",
    "orange": "warning",
    "yellow": "warning",
    "blue": "info",
    "cyan": "info",
}

MUTED = "cfg-muted"
STRONG = "cfg-strong"
SMALL = "cfg-small"
MONO = "cfg-mono"
ROW = "cfg-row"
STACK = "cfg-stack"
CODE = "cfg-code"
ICON = "cfg-icon"
KV = "cfg-kv"
PROGRESS = "cfg-progress"
PROGRESS_LABELS = "cfg-progress-labels"


def tone(value: Any, default: str = "info") -> str:
    """Normalise a variant/colour name (or ``BadgeVariant``) to one of ``TONES``."""
    if value is None:
        return default
    name = str(getattr(value, "value", value)).strip().lower()
    name = _TONE_ALIASES.get(name, name)
    return name if name in TONES else default


def badge(value: Any, default: str = "info") -> str:
    """``cfg-badge cfg-badge--<tone>``."""
    return f"cfg-badge cfg-badge--{tone(value, default)}"


def text_tone(value: Any) -> str:
    """Text colour class for a tone: ``cfg-success`` ..., ``cfg-muted`` for neutral, '' for none."""
    if value is None or value == "":
        return ""
    t = tone(value, default="")
    if not t:
        return ""
    if t == "neutral":
        return MUTED
    return f"cfg-{t}"


def box(value: Any = None) -> str:
    """``cfg-box`` with an optional tone modifier (success/warning/danger/info)."""
    t = tone(value, default="")
    if t in ("success", "warning", "danger", "info"):
        return f"cfg-box cfg-box--{t}"
    return "cfg-box"


def join(*classes: str) -> str:
    """Join non-empty class names with single spaces."""
    return " ".join(c for c in classes if c)


__all__ = [
    "TONES", "MUTED", "STRONG", "SMALL", "MONO", "ROW", "STACK", "CODE", "ICON",
    "KV", "PROGRESS", "PROGRESS_LABELS", "tone", "badge", "text_tone", "box", "join",
]
