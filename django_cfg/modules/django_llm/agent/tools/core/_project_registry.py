"""ProjectToolRegistry — per-project tool injection for public chat sessions.

Any Django app can register tools for a specific KB project slug via
``project_tool_registry.register(slug, tools)``. The CRM chat registry
then calls ``project_tool_registry.get(slug)`` to extend ``public_tools``
without knowing anything about the registering app.

Registration happens in ``AppConfig.ready()`` of each product app.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class ProjectToolRegistry:
    """Singleton registry mapping KB project slugs to extra public tools.

    Thread safety: registration happens at Django startup (single-threaded
    import phase). Read-only at request time — no locks needed.
    """

    def __init__(self) -> None:
        self._registry: dict[str, list[Any]] = {}

    def register(self, project_slug: str, tools: list[Any]) -> None:
        """Register a list of tool callables for a KB project slug.

        Safe to call multiple times — subsequent calls extend the list.

        Args:
            project_slug: Slug of the KnowledgeBaseProject (e.g. "vamcar").
            tools: List of tool callables (as returned by BaseTool.as_callable()).
        """
        existing = self._registry.setdefault(project_slug, [])
        existing.extend(tools)
        logger.debug(
            "[project_tool_registry] registered %d tools for slug=%r (total=%d)",
            len(tools), project_slug, len(existing),
        )

    def get(self, project_slug: str) -> list[Any]:
        """Return extra tools for the given slug (empty list if none registered)."""
        return list(self._registry.get(project_slug, []))

    def slugs(self) -> list[str]:
        """Return all slugs that have tools registered."""
        return list(self._registry.keys())


project_tool_registry = ProjectToolRegistry()
