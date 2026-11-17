"""Fill a lead with what the project already knows about itself (``get_current_config``).

Nothing here is asked of the form: the project name becomes the Brand when the adapter set none, and the environment,
site and API host go to Details. A lead from a dev or staging machine is then visibly not a real one.
The request that saved the lead adds the page (Referer), campaign parameters (UTM, gclid) and language.
Values the adapter set itself are never overwritten.
"""

from __future__ import annotations

from urllib.parse import urlsplit

from django_cfg.core.state import get_current_config

from . import context
from .lead import NotionLead


def _host(url: str) -> str:
    return urlsplit(url or "").netloc


def enrich(lead: NotionLead) -> NotionLead:
    config = get_current_config()
    if config is None:
        return lead
    extra = dict(lead.extra)
    env_mode = getattr(config, "env_mode", None)
    for label, value in (
        ("Project", getattr(config, "project_name", "")),
        ("Environment", getattr(env_mode, "value", env_mode) or ""),
        ("Site", _host(getattr(config, "site_url", ""))),
        ("API host", _host(getattr(config, "api_url", ""))),
    ):
        if value and label not in extra:
            extra[label] = str(value)
    request = context.get()
    for label, value in {**request.get("campaign", {}), "Locale": request.get("locale", "")}.items():
        if value and label not in extra:
            extra[label] = value
    return lead.model_copy(update={
        "brand": lead.brand or getattr(config, "project_name", "") or "",
        "page_url": lead.page_url or request.get("page_url", ""),
        "extra": extra,
    })
