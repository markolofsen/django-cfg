"""TierToolRegistry — register tools into specific permission tiers.

Used by project-side overlays (apps/ext/<module>/) that add tools to the
CRM AI agent without modifying CRM core. Mirrors ``ProjectToolRegistry``
(which is per-KB-project / public chat); this one is per-permission-tier
(public / staff / superadmin × base / deferred).

Tiers
-----
``PUBLIC``
    Added to ``public_tools`` for unauthenticated / visitor chat.

``STAFF_BASE`` / ``SUPERADMIN_BASE``
    Always visible to the model from turn 1. Mutations belong here —
    deferring them causes cheap models to hallucinate "task created"
    without an actual tool call.

``STAFF_DEFERRED`` / ``SUPERADMIN_DEFERRED``
    Hidden behind ``search_tools(keywords=...)``. Saves prompt tokens.
    Only safe for reads with no side effects.

Registration happens in ``AppConfig.ready()`` of each overlay app.
"""

from __future__ import annotations

import enum
import logging
from typing import Any

logger = logging.getLogger(__name__)


class ToolTier(str, enum.Enum):
    PUBLIC = "public"
    STAFF_BASE = "staff_base"
    STAFF_DEFERRED = "staff_deferred"
    SUPERADMIN_BASE = "superadmin_base"
    SUPERADMIN_DEFERRED = "superadmin_deferred"


class TierToolRegistry:
    """Singleton registry mapping ToolTier → list of tool callables.

    Thread safety: registration happens at Django startup (single-threaded
    import phase). Read-only at request time — no locks needed.
    """

    def __init__(self) -> None:
        self._registry: dict[ToolTier, list[Any]] = {t: [] for t in ToolTier}

    def register(self, tier: ToolTier, tools: list[Any]) -> None:
        """Register a list of tool callables for the given tier.

        Safe to call multiple times — subsequent calls extend the tier.
        """
        if not isinstance(tier, ToolTier):
            raise TypeError(f"tier must be ToolTier, got {type(tier).__name__}")
        self._registry[tier].extend(tools)
        logger.debug(
            "[tier_tool_registry] registered %d tools for tier=%s (total=%d)",
            len(tools), tier.value, len(self._registry[tier]),
        )

    def get(self, tier: ToolTier) -> list[Any]:
        """Return tools registered for the given tier (empty list if none)."""
        return list(self._registry[tier])

    def deferred_names(self) -> frozenset[str]:
        """Names of every tool registered in any DEFERRED tier.

        Used by ``get_toolsets_for_deps`` to split base / deferred when the
        legacy ``_STAFF_DEFERRED`` / ``_SUPERADMIN_DEFERRED`` frozensets are
        merged with overlay-registered deferred tools.
        """
        names: list[str] = []
        for tier in (ToolTier.STAFF_DEFERRED, ToolTier.SUPERADMIN_DEFERRED):
            for fn in self._registry[tier]:
                name = getattr(fn, "__name__", "")
                if name:
                    names.append(name)
        return frozenset(names)


tier_tool_registry = TierToolRegistry()
