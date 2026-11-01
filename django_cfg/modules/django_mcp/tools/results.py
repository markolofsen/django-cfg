"""What a tool may return beyond a string: extra content blocks.

``MCPTool.execute()`` returns ``str`` (one text block, as always) or a
``ToolResult`` when the tool also wants to attach an image or a link. The shape
follows MCP 2025-06-18: ``content[].type`` is one of ``text``, ``image``,
``audio``, ``resource_link`` or ``resource``.
"""

from __future__ import annotations

import base64
from dataclasses import dataclass, field
from typing import Any, Dict, List

ContentBlock = Dict[str, Any]

BLOCK_TYPES = frozenset({"text", "image", "audio", "resource_link", "resource"})

#: Default cap on the base64 payload of all blocks in one result, per profile
#: (``MCPProfile.max_block_bytes``).
DEFAULT_MAX_BLOCK_BYTES = 1_000_000


def image_block(data: bytes, mime: str) -> ContentBlock:
    """An inline image: ``data`` is raw bytes, the wire form is base64."""
    return {"type": "image", "mimeType": mime, "data": base64.b64encode(data).decode("ascii")}


def audio_block(data: bytes, mime: str) -> ContentBlock:
    return {"type": "audio", "mimeType": mime, "data": base64.b64encode(data).decode("ascii")}


def resource_link_block(uri: str, name: str, mime: str | None = None) -> ContentBlock:
    """A link the client may fetch itself: costs no payload."""
    block: ContentBlock = {"type": "resource_link", "uri": uri, "name": name}
    if mime:
        block["mimeType"] = mime
    return block


def blocks_size(blocks: List[ContentBlock]) -> int:
    """Wire size of the inline payloads (base64 characters) in ``blocks``."""
    return sum(len(b.get("data") or "") for b in blocks)


@dataclass
class ToolResult:
    """Text plus extra blocks. The text block always comes first."""

    text: str
    blocks: List[ContentBlock] = field(default_factory=list)
    is_error: bool = False

    def __post_init__(self) -> None:
        for block in self.blocks:
            kind = block.get("type")
            if kind not in BLOCK_TYPES:
                raise ValueError(f"Unknown content block type {kind!r}; expected one of {sorted(BLOCK_TYPES)}")
