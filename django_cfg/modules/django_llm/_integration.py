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
`get_api_keys()` is the **single config accessor** for the whole module:
every client (`LLMClient`, vision, image-gen, translator) and the model
registry read provider keys through it — never from the host directly.

Config comes from `get_current_config()`, the thread-local registry that
`set_current_config()` populates. That is the one place a `DjangoConfig`
is published, so it is the one place this module reads.
"""

from __future__ import annotations

import logging
import os

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


#: Provider slots the module always reports, so a caller can test membership
#: rather than guess. A slot with no credential is `None`, never absent.
_PROVIDER_SLOTS: tuple[str, ...] = ("openrouter", "openai", "sdkrouter")

#: Env override per slot, checked BEFORE config. `sdkrouter` is a transport
#: token rather than a vendor credential, so a deployment can point at a proxy
#: without waiting on a config release.
_ENV_VARS: dict[str, str] = {
    "openrouter": "DJANGO_LLM_KEYS__OPENROUTER",
    "openai": "DJANGO_LLM_KEYS__OPENAI",
    "sdkrouter": "DJANGO_LLM_KEYS__SDKROUTER",
}


def get_api_keys() -> dict[str, str | None]:
    """Return the LLM provider API keys the module should use.

    The single source of truth for credentials — every client and the model
    registry call this; nothing reads host config on its own.

    **Env first, config second.** A deployment can redirect a provider without
    a config release, and a test can set one variable and have it hold — with
    config first, `monkeypatch.setenv` loses to a checked-in key and the test
    silently compares a real credential against its fixture.

    Config comes from `get_current_config()` — the registry `set_current_config`
    publishes to. Reading it anywhere else means a second, divergent view of
    what the config is.
    """
    keys: dict[str, str | None] = {name: None for name in _PROVIDER_SLOTS}

    for name in _PROVIDER_SLOTS:
        value = os.environ.get(_ENV_VARS[name])
        if value:
            keys[name] = value

    try:
        api_keys = getattr(get_current_config(), "api_keys", None)
        if api_keys is not None:
            for name in _PROVIDER_SLOTS:
                if keys[name]:
                    continue  # env already answered
                # Prefer the accessor (it applies its own env fallback); a slot
                # django_cfg's ApiKeys does not define simply stays None.
                getter = getattr(api_keys, f"get_{name}_key", None)
                value = getter() if callable(getter) else getattr(api_keys, name, None)
                keys[name] = str(value) if value else None
    except Exception as exc:
        logger.warning(
            "Could not read LLM API keys from the config registry: %s. "
            "LLM/monitoring calls will run without credentials.",
            exc,
        )
    return keys
