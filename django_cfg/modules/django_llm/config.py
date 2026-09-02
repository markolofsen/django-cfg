"""Standalone configuration and host integration for :mod:`modules.django_llm`.

Clients use a hybrid configuration model:

  * clients accept EXPLICIT args (`LLMClient(api_key=...)`) — testable, no globals,
    multi-tenant friendly; an explicit value always wins;
  * when omitted, they fall back to ENV via a self-contained pydantic-settings
    object (``LLMConfig``). The package has no Django dependency.

Env (all optional; explicit args override):
    CMDOP_PROJECT_NAME, CMDOP_ENVIRONMENT
    CMDOP_LLM_KEYS__OPENROUTER | OPENROUTER_API_KEY
    CMDOP_LLM_KEYS__OPENAI     | OPENAI_API_KEY
    CMDOP_TELEGRAM_BOT_TOKEN, CMDOP_TELEGRAM_CHAT_ID, CMDOP_TELEGRAM_PARSE_MODE

`BaseCfgModule` is the framework-neutral base the ported clients subclass; its
`get_config()` returns the env-backed config (or a host-injected one).
"""

from __future__ import annotations

import logging
import os
import threading
import time
from functools import lru_cache
from typing import Any, Callable

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def get_logger(name: str) -> logging.Logger:
    """stdlib logger (the ports import `get_logger` from the host)."""
    return logging.getLogger(name)


# --- env-backed settings (the fallback when a caller passes nothing) ---------


class _TelegramSettings(BaseModel):
    bot_token: str | None = None
    chat_id: str | int | None = None
    parse_mode: str | None = "Markdown"


class APIKeys(BaseModel):
    openrouter: str | None = None
    openai: str | None = None
    # The cmdop token for the edge proxy (`llm.sdkrouter.com`). Distinct from the
    # two above in kind, not just in value: those are VENDOR credentials that
    # work against a vendor directly, this one works nowhere else. That is the
    # point of the proxy — a leaked cmdop token buys an attacker our proxy, not
    # our OpenRouter balance.
    sdkrouter: str | None = None

    def get_openrouter_key(self) -> str | None:
        return self.openrouter

    def get_openai_key(self) -> str | None:
        return self.openai

    def get_sdkrouter_key(self) -> str | None:
        return self.sdkrouter


class LLMConfig(BaseSettings):
    """Self-contained env-driven config for the ported features.

    Nested keys use the ``CMDOP_LLM_KEYS__OPENROUTER`` style; plain ``OPENROUTER_API_KEY`` /
    `OPENAI_API_KEY` are also honored (see `_load_from_env`).
    """

    model_config = SettingsConfigDict(
        env_prefix="CMDOP_",
        env_nested_delimiter="__",
        extra="ignore",
    )

    project_name: str = "cmdop"
    environment: str = ""
    telegram: _TelegramSettings = Field(default_factory=_TelegramSettings)
    api_keys: APIKeys = Field(default_factory=APIKeys)

    @property
    def is_development(self) -> bool:
        return self.environment == "dev"

    @property
    def is_test(self) -> bool:
        return self.environment == "test"


def _load_from_env() -> LLMConfig:
    """Build an LLMConfig, applying the plain *_API_KEY fallbacks pydantic's
    nested env parsing doesn't cover."""
    cfg = LLMConfig()
    env = os.environ.get
    if not cfg.api_keys.openrouter:
        cfg.api_keys.openrouter = (
            env("CMDOP_LLM_KEYS__OPENROUTER")
            or env("CMDOP_DEV_LLM_KEYS__OPENROUTER")
            or env("OPENROUTER_API_KEY")
        )
    if not cfg.api_keys.openai:
        cfg.api_keys.openai = (
            env("CMDOP_LLM_KEYS__OPENAI")
            or env("CMDOP_DEV_LLM_KEYS__OPENAI")
            or env("OPENAI_API_KEY")
        )
    if not cfg.api_keys.sdkrouter:
        cfg.api_keys.sdkrouter = (
            env("CMDOP_LLM_KEYS__SDKROUTER")
            or env("CMDOP_DEV_LLM_KEYS__SDKROUTER")
            or env("CMDOP_LLM_PROXY_TOKEN")
        )
    if not cfg.telegram.bot_token:
        cfg.telegram.bot_token = env("CMDOP_TELEGRAM_BOT_TOKEN")
    if not cfg.telegram.chat_id:
        cfg.telegram.chat_id = env("CMDOP_TELEGRAM_CHAT_ID")
    return cfg


# Process-wide config (the env fallback). Host may override via set_config().
_config: Any | None = None


def set_config(config: Any) -> None:
    """Inject a config (a host app can supply its own instead of the env one)."""
    global _config
    _config = config


def get_config() -> Any:
    """The env-backed (or host-injected) config — the FALLBACK path. Prefer
    passing explicit args to clients; this is what they read when you don't."""
    global _config
    if _config is None:
        _config = _load_from_env()
    return _config


def reset_config() -> None:
    global _config
    _config = None


class BaseCfgModule:
    """Framework-neutral replacement for django_cfg's `BaseCfgModule`.

    The ported clients subclass this and use construction + `get_config()` /
    `self.config` as the env fallback when no explicit value was passed.
    """

    def __init__(self) -> None:  # noqa: B027 - intentional no-op (parity w/ super().__init__())
        pass

    @classmethod
    def get_config(cls) -> Any:
        return get_config()

    def set_config(self, config: Any) -> None:
        set_config(config)

    @property
    def config(self) -> Any:
        return get_config()


# --- tiny TTL cache (replaces django.core.cache in monitoring) --------------


class _CacheShim:
    """Minimal get/set/delete over a process-local TTLCache — the subset the
    ported monitoring used from django.core.cache (no cross-process sharing; a
    host can swap this for Redis later)."""

    def __init__(self) -> None:
        self._values: dict[str, tuple[float | None, Any]] = {}
        self._lock = threading.RLock()

    def get(self, key: str, default: Any = None) -> Any:
        with self._lock:
            item = self._values.get(key)
            if item is None:
                return default
            expires_at, value = item
            if expires_at is not None and expires_at <= time.monotonic():
                self._values.pop(key, None)
                return default
            return value

    def set(self, key: str, value, timeout: int | None = None) -> None:  # noqa: A002
        expires_at = time.monotonic() + timeout if timeout is not None else None
        with self._lock:
            self._values[key] = (expires_at, value)

    def delete(self, key: str) -> None:
        with self._lock:
            self._values.pop(key, None)


cache = _CacheShim()


NotificationHandler = Callable[[str, str, dict[str, Any]], dict[str, bool] | None]
_notification_handler: NotificationHandler | None = None


def set_notification_handler(handler: NotificationHandler | None) -> None:
    """Register a host-owned email/Telegram/etc. notification callback."""
    global _notification_handler
    _notification_handler = handler


def notify(*, subject: str, message: str, context: dict[str, Any]) -> dict[str, bool]:
    """Invoke the configured notification callback; default to a safe no-op."""
    if _notification_handler is None:
        return {"email": False, "telegram": False}
    try:
        return _notification_handler(subject, message, context) or {
            "email": False,
            "telegram": False,
        }
    except Exception:
        logging.getLogger("modules.django_llm").exception("Notification handler failed")
        return {"email": False, "telegram": False}


# Backward-compatible name used by the first extraction from cmdop-utils.
CompatConfig = LLMConfig


__all__ = [
    "APIKeys",
    "BaseCfgModule",
    "CompatConfig",
    "LLMConfig",
    "cache",
    "get_config",
    "notify",
    "reset_config",
    "set_config",
    "set_notification_handler",
]
