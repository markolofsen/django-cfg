"""The project's `ChatConfig`, read when needed (never cached: a test or an env switch may change it)."""

from __future__ import annotations

from django_cfg.models.django.chat import ChatConfig


def chat_config() -> ChatConfig:
    from django_cfg.modules.base import BaseCfgModule

    found = BaseCfgModule()._get_config_key("chat", None)
    return found if isinstance(found, ChatConfig) else ChatConfig(enabled=False)
