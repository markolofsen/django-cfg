"""
django_llm — host integration seam.

This is the **only** file in `django_llm` that imports from the host
environment. Every external dependency the module needs — the config base
class, the Telegram notifier — is funneled through here and re-exported;
every other file imports these names from here with a stable
package-relative import (`from .._integration import ...`).

Why this exists
---------------
`django_llm` lives inside `django_cfg.modules`, but keeps host-coupled
imports confined to this single file so the module stays self-contained and
easy to relocate. Every other file imports these names from here.

API keys
--------
API keys currently reach the module through `BaseCfgModule.get_config()`
(django_cfg's `DjangoConfig`). If key access is later sourced elsewhere,
wire it here via `get_api_keys()` — this stays the single place to change.
"""

from __future__ import annotations

import logging

# --- Host: django_cfg -- the only host-coupled imports in the module -------
from ..base import BaseCfgModule
from ..django_telegram import DjangoTelegram
from ...core.config import get_current_config
from ..django_email import send_admin_notification

logger = logging.getLogger("django_cfg.django_llm")

__all__ = [
    "BaseCfgModule",
    "DjangoTelegram",
    "get_current_config",
    "send_admin_notification",
    "get_api_keys",
]


def get_api_keys() -> dict[str, str | None]:
    """Return the LLM provider API keys the module should use.

    Single source of truth for credentials. Today it reads django_cfg's
    `DjangoConfig` (the same path `BaseCfgModule`-based clients already
    use). To source keys from carapis `api/environment` instead, change
    only this function — e.g.::

        from api.environment import env
        return {"openrouter": env.llm.openrouter_key,
                "openai": env.llm.openai_key}
    """
    keys: dict[str, str | None] = {"openrouter": None, "openai": None}
    try:
        config = BaseCfgModule().get_config()
        api_keys = getattr(config, "api_keys", None)
        if api_keys is not None:
            keys["openrouter"] = getattr(api_keys, "openrouter", None)
            keys["openai"] = getattr(api_keys, "openai", None)
    except Exception as exc:
        logger.warning(
            "Could not read LLM API keys from django_cfg config: %s. "
            "LLM/monitoring calls will run without credentials.",
            exc,
        )
    return keys
