"""Tool authoring for the agent plane.

`core/` is the mechanism: `BaseTool`, the `@llm_tool` decorator, `ToolMeta`, the
LLM serializer, and the tier/project registries. It has **zero Django-app
dependencies** — only pydantic and pydantic-ai — which is what made it liftable out
of CRM in the first place.

A host's actual tools (the ones that name its models) are NOT here. They live in the
host and reach an agent through the `ToolProvider` Protocol.
"""

from __future__ import annotations

__all__: list[str] = []
