"""TypedDicts for stacked display config (local re-export for renderer imports)."""
from __future__ import annotations

# Re-export from parent _types so renderers can import from their package
from .._types import BadgeRendererConfig, DateTimeItemConfig, MoneyItemConfig, TextRendererConfig

__all__ = ["TextRendererConfig", "BadgeRendererConfig", "DateTimeItemConfig", "MoneyItemConfig"]
