"""MCP registry tools as pydantic-ai tools for an agent run.

A remote app's tools (``remote.ProxyTool``) and local ``MCPTool``s live in
``tool_registry``. This module hands a chosen subset to a pydantic-ai ``Agent``.

**Deny by default.** The registry also holds operator tools (model queries, user
info). A chat for end users must never get them by accident, so at least one of
``prefix``, ``names`` or ``profile`` is required; several narrow together.

* the model-facing schema is the tool's MCP ``inputSchema``;
* the MCP user comes from ``context`` (an ``MCPContext``, or a callable returning one),
  never from the model's arguments;
* ``execute`` runs in a thread (it may be a blocking HTTP call);
* image blocks reach the model as ``BinaryContent`` (over ``max_image_bytes`` they are
  dropped with a note); other blocks become a short text line; an error result is
  returned as ``error: ...`` text so the model sees it;
* MCP annotations become a ``ToolMeta`` (``meta_from_annotations``) stamped like ``@llm_tool`` does.
"""

from __future__ import annotations

import base64
import logging
from collections.abc import Callable, Iterable
from typing import Any

from asgiref.sync import sync_to_async

from django_cfg.modules.django_mcp.services.context import MCPContext
from django_cfg.modules.django_mcp.tools.base import tool_registry
from django_cfg.modules.django_mcp.tools.results import ToolResult

logger = logging.getLogger(__name__)

#: Inline image budget per tool call (decoded bytes).
DEFAULT_MAX_IMAGE_BYTES = 1_000_000


def meta_from_annotations(annotations: dict[str, Any] | None):
    """``ToolMeta`` for MCP annotations.

    ``readOnlyHint`` true -> category ``read`` (``openWorldHint`` does not change it: a web
    lookup is still a read); otherwise ``mutation``. ``customer_visible`` follows
    ``openWorldHint`` for a writer (it reaches outside this system). A tool with no
    annotations is a ``mutation``, the same safe default MCP clients apply.
    """
    from django_cfg.modules.django_llm.agent.tools.core._meta import ToolMeta

    hints = annotations or {}
    if hints.get("readOnlyHint"):
        return ToolMeta(category="read")
    return ToolMeta(category="mutation", customer_visible=bool(hints.get("openWorldHint")))


def _context(context: Any) -> MCPContext:
    value = context() if callable(context) and not isinstance(context, MCPContext) else context
    if isinstance(value, MCPContext):
        return value
    return MCPContext(user=value, request=None, session_key="agent", config=None)


def to_model_content(result: Any, max_image_bytes: int) -> Any:
    """A tool result as a pydantic-ai return value: text, or ``ToolReturn`` with images."""
    from pydantic_ai import BinaryContent, ToolReturn

    if not isinstance(result, ToolResult):
        return str(result)
    lines = [result.text] if result.text else []
    images: list[Any] = []
    for block in result.blocks:
        kind = block.get("type")
        if kind == "image":
            try:
                raw = base64.b64decode(block.get("data") or "", validate=True)
            except ValueError:
                lines.append("[image dropped: not valid base64]")
                continue
            if len(raw) > max_image_bytes:
                lines.append(f"[image dropped: {len(raw)} bytes is over the {max_image_bytes} byte limit]")
            else:
                images.append(BinaryContent(data=raw, media_type=block.get("mimeType") or "image/png"))
        elif kind == "resource_link":
            lines.append(f"[link: {block.get('name') or block.get('uri')}]")
        elif kind in ("audio", "resource"):
            lines.append(f"[{kind} block omitted]")
    text = "\n".join(lines)
    if result.is_error:
        return f"error: {text}"
    return ToolReturn(return_value=text, content=images) if images else text


def _make_tool(mcp_tool: Any, name: str, context: Any, max_image_bytes: int):
    from pydantic_ai import Tool

    async def call(**arguments: Any) -> Any:
        ctx = _context(context)
        result = await sync_to_async(mcp_tool.execute, thread_sensitive=False)(ctx, arguments)
        return to_model_content(result, max_image_bytes)

    call.__name__ = name
    from django_cfg.modules.django_llm.agent.tools.core._meta import attach_meta

    attach_meta(call, meta_from_annotations(mcp_tool.annotations()))
    schema = mcp_tool.input_schema or {"type": "object", "properties": {}}
    tool = Tool.from_schema(call, name=name, description=mcp_tool.description or name, json_schema=schema)
    # ``Tool`` is not a function: keep the meta where the plane looks for it on both.
    attach_meta(tool, meta_from_annotations(mcp_tool.annotations()))
    return tool


def mcp_tools(
    *,
    prefix: str | None = None,
    names: Iterable[str] | None = None,
    profile: Any = None,
    context: Any = None,
    strip_prefix: bool = True,
    max_image_bytes: int = DEFAULT_MAX_IMAGE_BYTES,
) -> list[Any]:
    """pydantic-ai tools for the registry tools that pass every given filter.

    ``names`` match the registry name (with the prefix). ``strip_prefix`` drops ``prefix``
    from the name the model sees. Raises ``ValueError`` when no filter is given.
    """
    wanted = None if names is None else set(names)
    if prefix is None and wanted is None and profile is None:
        raise ValueError("mcp_tools needs a prefix, names or a profile: refusing to expose the whole registry")
    tools = tool_registry.get_all_tools(_probe_context(context), profile=profile)
    out = []
    for tool in tools:
        if prefix is not None and not tool.name.startswith(prefix):
            continue
        if wanted is not None and tool.name not in wanted:
            continue
        if profile is not None and not profile.serves(tool):
            continue
        shown = tool.name[len(prefix):] if prefix and strip_prefix else tool.name
        out.append(_make_tool(tool, shown, context, max_image_bytes))
    return out


def _probe_context(context: Any) -> MCPContext | None:
    try:
        return _context(context) if context is not None else None
    except Exception:  # noqa: BLE001 - listing must not depend on a per-request callable
        return None


class McpToolProvider:
    """The agent plane's ``ToolProvider`` over ``mcp_tools`` (same filters, same refusal)."""

    def __init__(self, **options: Any) -> None:
        mcp_tools_check = {k: options.get(k) for k in ("prefix", "names", "profile")}
        if all(v is None for v in mcp_tools_check.values()):
            raise ValueError("McpToolProvider needs a prefix, names or a profile")
        self._options = options

    def get_tools(self) -> list[Any]:
        return mcp_tools(**self._options)

    def get_toolsets(self) -> list[Any]:
        from pydantic_ai.toolsets import FunctionToolset

        return [FunctionToolset(self.get_tools())]
