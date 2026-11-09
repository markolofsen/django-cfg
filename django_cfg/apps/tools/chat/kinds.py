"""The default kind: instructions, model chain and (optionally) a knowledge folder, all from `ChatConfig`. No tools: a
project that needs tools registers its own kind with `django_llm.agent.chat.kind.register` and names it in a request."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from pathlib import Path

from django_cfg.apps.tools.chat.settings import chat_config
from django_cfg.models.django.chat import ChatConfig
from django_cfg.modules.django_llm.agent.chat import kind as kinds


@dataclass
class Deps:
    user_id: int
    thread_id: uuid.UUID
    instructions: str


def _knowledge(cfg: ChatConfig):
    from django.conf import settings

    from django_cfg.modules.django_llm.agent.chat.knowledge import Knowledge

    if cfg.knowledge_dir:
        path = Path(cfg.knowledge_dir)
        if not path.is_absolute():
            path = Path(str(getattr(settings, "BASE_DIR", "."))) / path
        return Knowledge(source=path, language=cfg.knowledge_language)
    if cfg.knowledge:
        return Knowledge(source=cfg.knowledge, language=cfg.knowledge_language)
    return None


def build_default_kind(cfg: ChatConfig) -> kinds.ChatKind:
    return kinds.ChatKind(
        name=cfg.default_kind,
        prompt_version="cfg-chat-1",
        models=tuple(cfg.models),
        build_instructions=lambda deps: deps.instructions,
        build_tools=lambda deps: [],
        make_deps=lambda scope: Deps(scope.user.pk, scope.thread_id, cfg.instructions),
        limits=kinds.KindLimits(max_tokens=cfg.max_tokens),
        history_window=cfg.history_window,
        knowledge=_knowledge(cfg),
        attachments=cfg.attachments.policy() if cfg.attachments is not None else None,
    )


def register_default_kind() -> kinds.ChatKind | None:
    """Register the configured default kind once; a kind of that name registered by the project wins."""
    cfg = chat_config()
    if not cfg.enabled:
        return None
    try:
        return kinds.get(cfg.default_kind)
    except kinds.UnknownKind:
        return kinds.register(build_default_kind(cfg))
