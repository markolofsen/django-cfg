"""The django-cfg admin site: the stock ``AdminSite`` plus our navigation and branding.

Installed through ``CfgAdminConfig.default_site`` (``apps.py``), so ``admin.site``
and ``@admin.register`` everywhere resolve to this class; projects edit nothing.

It reads the ``CFG_ADMIN_SITE`` settings dict that ``AdminSiteConfig.to_django_settings``
builds (titles, ``SIDEBAR.navigation``, ``SITE_DROPDOWN``, ``LOGIN``). Without that
dict it is the stock site titled from the project name.

Navigation is rendered by the stock sidebar: ``get_app_list()`` returns the
declared sections in the stock ``app_list`` shape, and our ``admin/app_list.html``
adds the icons and marks the current item.
"""

from __future__ import annotations

import logging
import re
from collections.abc import Iterable
from typing import Any

from django.conf import settings
from django.contrib import admin
from django.urls import NoReverseMatch, reverse
from django.utils.module_loading import import_string

logger = logging.getLogger(__name__)

_CHANGELIST = re.compile(r"^admin:(?P<app>[a-z0-9_]+)_(?P<model>[a-z0-9]+)_changelist$")

# Badge tone per environment mode (cfg-badge--<tone> in cfg-admin.css).
_ENV_TONES = {"production": "danger", "development": "info", "test": "warning"}


def _site_settings() -> dict[str, Any]:
    value = getattr(settings, "CFG_ADMIN_SITE", None)
    return value if isinstance(value, dict) else {}


def _project_name() -> str:
    try:
        from django_cfg.core.state import get_current_config

        config = get_current_config()
        return (getattr(config, "project_name", "") or "") if config else ""
    except Exception:  # noqa: BLE001 - branding must never break the admin
        return ""


def _call(value: Any, request) -> Any:
    """A setting value may be a plain value or a callable taking the request."""
    return value(request) if callable(value) else value


class CfgAdminSite(admin.AdminSite):
    """Stock admin site with django-cfg navigation, branding and login form."""

    # The Overview (dashboard tabs, MCP chat) is the index page only. It has its
    # own template name: Django's ``admin/app_index.html`` extends
    # ``admin/index.html``, so overriding that name put the Overview on every
    # ``/admin/<app_label>/`` page too. With the name left alone, app pages are
    # the stock model list of the app (``app_index_template`` stays ``None``).
    index_template = "admin/cfg_overview.html"

    # ---- branding ---------------------------------------------------------
    # Properties, so the values follow settings (tests override them) while an
    # explicit ``admin.site.site_header = ...`` in a project still wins.

    def _brand(self, key: str, attr: str, fallback: str) -> str:
        explicit = self.__dict__.get(attr)
        if explicit is not None:
            return explicit
        return _site_settings().get(key) or fallback

    @property
    def site_title(self) -> str:
        name = _project_name()
        return self._brand("SITE_TITLE", "_site_title", f"{name} Admin" if name else admin.AdminSite.site_title)

    @site_title.setter
    def site_title(self, value: str) -> None:
        self.__dict__["_site_title"] = value

    @property
    def site_header(self) -> str:
        return self._brand("SITE_HEADER", "_site_header", _project_name() or admin.AdminSite.site_header)

    @site_header.setter
    def site_header(self, value: str) -> None:
        self.__dict__["_site_header"] = value

    @property
    def site_url(self) -> str:
        return self._brand("SITE_URL", "_site_url", admin.AdminSite.site_url)

    @site_url.setter
    def site_url(self, value: str) -> None:
        self.__dict__["_site_url"] = value

    def each_context(self, request):
        context = super().each_context(request)
        site = _site_settings()
        context.update(
            {
                "cfg_site_subheader": site.get("SITE_SUBHEADER", ""),
                "cfg_site_symbol": site.get("SITE_SYMBOL", ""),
                "cfg_site_dropdown": self._site_dropdown(request, site),
                "cfg_environment": self._environment(),
            }
        )
        return context

    @staticmethod
    def _site_dropdown(request, site: dict[str, Any]) -> list[dict[str, str]]:
        items = []
        for raw in site.get("SITE_DROPDOWN") or []:
            try:
                link = _call(raw.get("link"), request)
                if link:
                    items.append({"title": raw.get("title", ""), "icon": raw.get("icon", ""), "link": str(link)})
            except Exception:  # noqa: BLE001
                logger.warning("django-cfg admin: site dropdown item %r skipped", raw, exc_info=True)
        return items

    @staticmethod
    def _environment() -> dict[str, str] | None:
        try:
            from django_cfg.core.state import get_current_config

            config = get_current_config()
            mode = getattr(config, "env_mode", None) if config else None
            mode = getattr(mode, "value", mode)  # an enum, or its value (use_enum_values)
        except Exception:  # noqa: BLE001
            mode = None
        if not mode:
            return None
        return {"label": str(mode), "tone": _ENV_TONES.get(str(mode), "neutral")}

    # ---- login ------------------------------------------------------------

    @property
    def login_form(self):
        """``CFG_ADMIN_SITE["LOGIN"]["form"]`` (DevAuthForm when dev autofill is set), else stock."""
        if "_login_form" in self.__dict__:
            return self.__dict__["_login_form"]
        path = (_site_settings().get("LOGIN") or {}).get("form")
        if not path:
            return None
        try:
            return import_string(path)
        except ImportError:
            logger.warning("django-cfg admin: login form %s cannot be imported; using the stock form", path)
            return None

    @login_form.setter
    def login_form(self, value) -> None:
        self.__dict__["_login_form"] = value

    # ---- navigation -------------------------------------------------------

    def _navigation(self, request) -> list[dict[str, Any]]:
        sidebar = _site_settings().get("SIDEBAR") or {}
        nav = sidebar.get("navigation")
        try:
            nav = _call(nav, request)
        except Exception:  # noqa: BLE001 - a broken menu must not take the admin down
            logger.error("django-cfg admin: navigation failed to build", exc_info=True)
            return []
        return list(nav or [])

    def _show_all_applications(self) -> bool:
        sidebar = _site_settings().get("SIDEBAR") or {}
        return bool(sidebar.get("show_all_applications", True))

    def _resolve_link(self, link: Any, request) -> str | None:
        link = _call(link, request)
        if not link or link == "#":
            return None
        link = str(link)
        if link.startswith(("/", "http://", "https://")):
            return link
        try:
            return reverse(link, current_app=self.name)
        except NoReverseMatch:
            return None

    @staticmethod
    def _allowed(item: dict[str, Any], request) -> bool:
        permission = item.get("permission")
        if isinstance(permission, str):
            try:
                permission = import_string(permission)
            except ImportError:
                logger.warning("django-cfg admin: permission callback %s not importable; item hidden", permission)
                return False
        if callable(permission):
            try:
                return bool(permission(request))
            except Exception:  # noqa: BLE001
                logger.warning("django-cfg admin: permission callback failed; item hidden", exc_info=True)
                return False
        # NavigationItem.to_dict() sets a callback for admin:*_changelist links; a raw
        # dict (``AdminSidebar.navigation``) may not, so apply the same rule here.
        match = _CHANGELIST.match(str(item.get("link") or ""))
        if match:
            user = request.user
            return user.is_superuser or user.has_perm(f"{match['app']}.view_{match['model']}")
        return True

    def _section_models(self, section: dict[str, Any], request) -> list[dict[str, Any]]:
        models = []
        for item in section.get("items") or []:
            if not isinstance(item, dict) or not self._allowed(item, request):
                continue
            try:
                url = self._resolve_link(item.get("link"), request)
            except Exception:  # noqa: BLE001
                url = None
            if not url:
                continue
            title = str(item.get("title") or "")
            models.append(
                {
                    "name": title,
                    "object_name": re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-") or "item",
                    "admin_url": url,
                    "add_url": None,
                    "view_only": False,
                    "perms": {},
                    "icon": item.get("icon") or "",
                    "cfg_external": url.startswith(("http://", "https://")),
                }
            )
        return models

    def _mark_current(self, app_list: Iterable[dict[str, Any]], path: str) -> None:
        """Mark the one item whose URL is the longest prefix of the path.

        The stock template tests ``admin_url in request.path``, so a link to the
        admin root (Overview) would light up on every page. Here the admin root
        only matches itself, and only the best match is current.
        """
        best, best_len = None, -1
        index = reverse("admin:index", current_app=self.name)
        for app in app_list:
            for model in app["models"]:
                url = model.get("admin_url") or ""
                if model.get("cfg_external") or not url:
                    continue
                hit = path == url if url == index else path.startswith(url)
                if hit and len(url) > best_len:
                    best, best_len = (app, model), len(url)
        if best:
            best[0]["cfg_current"] = True
            best[1]["cfg_current"] = True

    def get_app_list(self, request, app_label=None):
        stock = super().get_app_list(request, app_label)
        if app_label is not None:
            return stock  # app index pages stay stock
        sections = []
        named_urls = set()
        for index, section in enumerate(self._navigation(request)):
            if not isinstance(section, dict):
                continue
            models = self._section_models(section, request)
            if not models:
                continue
            named_urls.update(m["admin_url"] for m in models)
            sections.append(
                {
                    "name": section.get("title") or "",
                    "app_label": f"cfg-nav-{index}",
                    "app_url": models[0]["admin_url"],
                    "has_module_perms": True,
                    "models": models,
                    "icon": section.get("icon") or "",
                    "cfg_section": True,
                }
            )
        if not sections:
            return stock
        if self._show_all_applications():
            # Everything registered stays reachable: stock apps, minus the models a
            # section already links to.
            for app in stock:
                rest = [m for m in app["models"] if m.get("admin_url") not in named_urls]
                if rest:
                    sections.append({**app, "models": rest})
        self._mark_current(sections, request.path)
        return sections
