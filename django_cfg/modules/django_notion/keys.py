"""The project key: which project (product, brand) a lead or a client belongs to, across every CRM table.

The key is attribution, so the server sets it, never the visitor: ``NotionConfig.project_keys`` maps a django-cfg site
key (``DjangoConfig.sites``, resolved from the request by ``site_for``) to a project key. One backend may serve several
sites and so several keys. A key is a lowercase slug (``carapis``, ``mls-bali``).

``normalize`` is the matching rule the Hub uses (``projectKey()`` in reforms-hub ``packages/projects``): lowercase, keep
``[a-z0-9]`` only. ``mls-bali``, ``MLS Bali`` and ``MLSBali`` are the same project. The Notion ``Brand`` option of a lead is
the live option whose normalized name equals the key's, so the human name Notion shows is kept and no option is invented.
"""

from __future__ import annotations

import logging
import re
import time
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("django_cfg.modules.django_notion")

_SLUG = re.compile(r"^[a-z0-9][a-z0-9-]{0,62}$")
OPTIONS_TTL_SECONDS = 300.0  # a new Notion option is seen within this long, without a restart

_options: Dict[Tuple[str, str], Tuple[float, List[str]]] = {}


def normalize(name: Any) -> str:
    """The Hub's ``projectKey()``: lowercase, ``[a-z0-9]`` only."""
    return re.sub(r"[^a-z0-9]", "", str(name or "").lower())


def is_key(value: str) -> bool:
    return bool(_SLUG.match(value or ""))


def clean(value: Any) -> str:
    """A valid key, or "" (a bad value never reaches a mail header or a Notion option)."""
    text = str(value or "").strip().lower()
    return text if is_key(text) else ""


def for_site(site_key: str, cfg) -> str:
    """The key ``cfg.project_keys`` gives the django-cfg site ``site_key`` ("" when the site has none)."""
    return clean((cfg.project_keys or {}).get(site_key or "", ""))


def single_site_key() -> str:
    """The site key when the config declares exactly one site; "" otherwise (several sites: never guess)."""
    try:
        from django_cfg.core.site import sites

        registry = sites()
    except Exception:
        return ""
    return registry[0].key if len(registry) == 1 else ""


def for_object(obj: Any, cfg) -> str:
    """The key of a row being exported: the user's site when ``obj`` is a user, else the only site. "" when unknown."""
    try:
        from django.contrib.auth import get_user_model

        if isinstance(obj, get_user_model()):
            from django_cfg.core.site import _site_of_user, sites

            site = _site_of_user(obj, sites())
            if site is not None:
                return for_site(site.key, cfg)
    except Exception:
        pass
    return for_site(single_site_key(), cfg)


def match_option(key: str, options: List[str]) -> Optional[str]:
    """The one option whose normalized name is the key's; None for no match or for two (never guess)."""
    want = normalize(key)
    found = [o for o in options if want and normalize(o) == want]
    return found[0] if len(found) == 1 else None


def clear_cache() -> None:
    _options.clear()


def options(client, data_source_id: str, column: str) -> List[str]:
    """The live options of the multi_select ``column``, cached per data source for ``OPTIONS_TTL_SECONDS``. Raises on a failed read."""
    cache_key = (data_source_id, column)
    hit = _options.get(cache_key)
    if hit and time.monotonic() - hit[0] < OPTIONS_TTL_SECONDS:
        return hit[1]
    ds = client.data_sources.retrieve(data_source_id)
    spec = (ds.get("properties") or {}).get(column) or {}
    names = [o.get("name", "") for o in (spec.get("multi_select") or {}).get("options", []) if o.get("name")]
    _options[cache_key] = (time.monotonic(), names)
    return names


def brand_option(client, data_source_id: str, column: str, key: str) -> Optional[str]:
    """The ``Brand`` option for ``key`` on this data source, or None (no read access, no option, or two). Never raises."""
    try:
        names = options(client, data_source_id, column)
    except Exception as exc:
        logger.warning("django_notion: cannot read the %r options of %s (%s); Brand left empty for key %r",
                       column, data_source_id, type(exc).__name__, key)
        return None
    found = match_option(key, names)
    if found is None:
        logger.warning("django_notion: no single %r option matches project key %r on %s; Brand left empty", column, key, data_source_id)
    return found
