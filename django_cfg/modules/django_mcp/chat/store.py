"""Redis-backed MCP agent chat history store."""

from __future__ import annotations

import json
import uuid
from typing import Optional

from django.core.cache import cache

MCP_CHAT_KEY_PREFIX = "mcp_chat"
MCP_CHAT_DEFAULT_MAX_MESSAGES = 50
MCP_CHAT_DEFAULT_TTL = 86400  # 24h


def _history_key(user_id: int | str, session_id: str) -> str:
    return f"{MCP_CHAT_KEY_PREFIX}:{user_id}:{session_id}"


class RedisMCPChatStore:
    """
    Stores MCP agent chat messages in Django's default cache (Redis).

    Messages are stored newest-first for efficient prepend/trim.
    get_history() reverses to chronological order for the LLM.
    TTL is sliding — reset on every read and write.
    """

    def __init__(self, user_id: int | str, session_id: Optional[str] = None) -> None:
        self.user_id = user_id
        self.session_id = session_id or str(uuid.uuid4())

    @property
    def _key(self) -> str:
        return _history_key(self.user_id, self.session_id)

    def get_history(self, max_messages: int = MCP_CHAT_DEFAULT_MAX_MESSAGES) -> list[dict]:
        """Return messages in chronological order (oldest first). Resets TTL."""
        raw = cache.get(self._key)
        if raw is None:
            return []
        messages: list[dict] = json.loads(raw)
        result = list(reversed(messages[:max_messages]))
        cache.touch(self._key, MCP_CHAT_DEFAULT_TTL)
        return result

    def append_message(self, role: str, content: str) -> None:
        """Prepend message (newest-first storage), trim to max_messages, reset TTL."""
        raw = cache.get(self._key)
        messages: list[dict] = json.loads(raw) if raw else []
        messages.insert(0, {"role": role, "content": content})
        messages = messages[:MCP_CHAT_DEFAULT_MAX_MESSAGES]
        cache.set(self._key, json.dumps(messages), timeout=MCP_CHAT_DEFAULT_TTL)

    def clear(self) -> None:
        cache.delete(self._key)
