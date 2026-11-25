"""Fill a lead with what the project already knows about itself (``get_current_config``).

Nothing here is asked of the form. The project key comes from the server's config (``NotionConfig.project_keys``) for
the lead's site: the one the adapter declared, else the site of the request that saved it, else the only site of a
single-site project. A site without a key leaves the key empty; it is never guessed from the project name. The
environment, site and API host go to Details, so a lead from a dev or staging machine is visibly not a real one.
The request that saved the lead adds the page (Referer), campaign parameters (UTM, gclid) and language.
Values the adapter set itself are never overwritten.
"""

from __future__ import annotations

import logging
from urllib.parse import urlsplit

from django_cfg.core.state import get_current_config

from . import context, keys
from .lead import NotionLead

logger = logging.getLogger("django_cfg.modules.django_notion")


def _host(url: str) -> str:
    return urlsplit(url or "").netloc


def _project(lead: NotionLead, request: dict) -> tuple[str, str]:
    """(site key, project key) of the lead."""
    site = lead.site or request.get("site", "") or keys.single_site_key()
    if lead.project:
        key = keys.clean(lead.project)
        if not key:
            logger.warning("django_notion: adapter project key %r is not a slug; left empty", lead.project)
        return site, key
    try:
        from . import conf

        return site, keys.for_site(site, conf.get_notion_config())
    except Exception:
        return site, ""


def with_project(lead: NotionLead) -> NotionLead:
    """The lead with its site and project key resolved. Runs even with ``NotionConfig.enrich`` off: the key is not optional."""
    site, project = _project(lead, context.get())
    return lead.model_copy(update={"site": site, "project": project})


def enrich(lead: NotionLead) -> NotionLead:
    config = get_current_config()
    if config is None:
        return with_project(lead)
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
    site, project = _project(lead, request)
    for label, value in {**request.get("campaign", {}), "Locale": request.get("locale", "")}.items():
        if value and label not in extra:
            extra[label] = value
    return lead.model_copy(update={
        "site": site,
        "project": project,
        "page_url": lead.page_url or request.get("page_url", ""),
        "extra": extra,
    })
