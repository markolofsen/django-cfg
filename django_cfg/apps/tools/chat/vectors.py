"""The ready app's vectorisation: `ChatConfig` supplies the switch and the numbers, `agent.chat.vectors` does the work."""

from __future__ import annotations

from typing import Any

from django_cfg.apps.tools.chat.settings import chat_config
from django_cfg.modules.django_llm.agent.chat.vectors import service
from django_cfg.modules.django_llm.agent.chat.vectors.embedder import Embedder, llm_embedder


def enabled() -> bool:
    cfg = chat_config()
    return cfg.enabled and cfg.vectors


def embedder() -> Embedder:
    return llm_embedder(chat_config().vector_model)


def sync(limit: int = 200, embed: Embedder | None = None) -> dict[str, Any]:
    from django_cfg.apps.tools.chat.models import ThreadChunk

    if not enabled():
        return {"enabled": False}
    cfg = chat_config()
    done = service.sync_pending(
        ThreadChunk, embed or embedder(), limit=limit,
        model=cfg.vector_model, max_messages=cfg.vector_chunk_messages, token_budget=cfg.vector_token_budget,
    )
    return {"enabled": True, **vars(done)}


def search(user, query: str, *, kind: str | None = None, limit: int = 8, embed: Embedder | None = None) -> list[service.Hit]:
    from django_cfg.apps.tools.chat.models import ThreadChunk

    return service.search(ThreadChunk, query, embed or embedder(), owner=user, kind=kind, limit=limit)
