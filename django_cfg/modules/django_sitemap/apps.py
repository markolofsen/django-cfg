"""Django AppConfig — autoloads each installed app's `sitemap_sources` module.

Apps that want to contribute sitemap URLs simply create a
`sitemap_sources.py` at the package root. The autoloader catches it on
`ready()`, the same way `django.contrib.admin` autodiscovers `admin.py`.
"""
from __future__ import annotations

import importlib
import logging

from django.apps import AppConfig, apps

logger = logging.getLogger(__name__)


class SitemapAppConfig(AppConfig):
    name = "django_cfg.modules.django_sitemap"
    label = "django_sitemap"
    verbose_name = "Sitemap"

    def ready(self) -> None:
        for app_config in apps.get_app_configs():
            module_name = f"{app_config.name}.sitemap_sources"
            try:
                importlib.import_module(module_name)
            except ModuleNotFoundError as exc:
                # Only swallow "this app has no sitemap_sources" — re-raise
                # if a *dependency* of sitemap_sources is missing.
                if exc.name == module_name:
                    continue
                raise
            else:
                logger.debug("django_sitemap: loaded sources from %s", module_name)
