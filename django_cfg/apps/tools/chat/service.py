"""`ChatService` over the app's tables, its policy read from `ChatConfig` on every use."""

from __future__ import annotations

from functools import lru_cache

from django_cfg.apps.tools.chat.settings import chat_config
from django_cfg.modules.django_llm.agent.chat.limits import TokenBreaker
from django_cfg.modules.django_llm.agent.chat.service import ChatPolicy, ChatService

breaker = TokenBreaker(budget=lambda: chat_config().daily_token_budget, key="cfg_chat:tokens:{day}")


def policy() -> ChatPolicy:
    cfg = chat_config()
    return ChatPolicy(
        messages_per_day=cfg.messages_per_day,
        max_text_chars=cfg.max_text_chars,
        title_models=tuple(cfg.title_models) or None,
        available=lambda: not chat_config().paused and breaker.available(),
    )


@lru_cache(maxsize=1)
def get_service() -> ChatService:
    from django_cfg.apps.tools.chat.models import Thread

    return ChatService(Thread, policy, on_answer=breaker.on_answer)
