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
It sources keys from `BaseCfgModule.get_config()` today; to switch to
another source, change only that function.
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

    The single source of truth for credentials — every `django_llm`
    client and the model registry call this; nothing reads host config
    on its own. Today it reads django_cfg's `DjangoConfig`. To source
    keys from another place, change only this body.

    Prefers the `api_keys.get_*_key()` accessor methods (which apply the
    env-var fallback) over the plain attributes.
    """
    keys: dict[str, str | None] = {"openrouter": None, "openai": None}
    try:
        api_keys = getattr(BaseCfgModule().get_config(), "api_keys", None)
        if api_keys is not None:
            for name in ("openrouter", "openai"):
                # Prefer the accessor method (applies env-var fallback);
                # fall back to the plain attribute.
                getter = getattr(api_keys, f"get_{name}_key", None)
                value = getter() if callable(getter) else getattr(api_keys, name, None)
                keys[name] = str(value) if value else None
    except Exception as exc:
        logger.warning(
            "Could not read LLM API keys from django_cfg config: %s. "
            "LLM/monitoring calls will run without credentials.",
            exc,
        )
    return keys
