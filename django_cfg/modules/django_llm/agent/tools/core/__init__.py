"""Core tooling for agent tools — decorator, meta, serialization, base schemas.

Zero Django app dependencies (only pydantic / pydantic-ai). Imported by every tool
file; never contains business logic.

That property is why this package could be lifted out of CRM unchanged: it was
already generic, and only its *location* said otherwise. It now lives in the agent
plane, and CRM imports it from here.

A tool reaches an agent by being named in a host's `ToolProvider`, or by being
registered with `tier_tool_registry` / `project_tool_registry`. **There is no
auto-discovery** — the old `ToolRegistry` collected 82 `@register` decorations into a
dict that nothing outside itself ever read, so 82 tools paid a decorator for a
mechanism with no consumer. Removed 2026-07-14; do not reintroduce it.
"""

from ._base_tool import BaseTool, strip_raw
from ._decorator import llm_tool
from ._meta import (
    ToolMeta,
    attach_meta,
    attach_sandbox_callable,
    get_sandbox_callable,
    get_tool_meta,
)
from ._project_registry import ProjectToolRegistry, project_tool_registry
from ._serialize import serialize_for_llm
from ._tier_registry import TierToolRegistry, ToolTier, tier_tool_registry
from ._validators import parse_uuid
from .schemas.base import ToolError

__all__ = [
    "BaseTool",
    "strip_raw",
    "llm_tool",
    "ToolMeta",
    "attach_meta",
    "get_tool_meta",
    "attach_sandbox_callable",
    "get_sandbox_callable",
    "ProjectToolRegistry",
    "project_tool_registry",
    "TierToolRegistry",
    "ToolTier",
    "tier_tool_registry",
    "serialize_for_llm",
    "parse_uuid",
    "ToolError",
]
