"""Django app configuration for the analytics app."""

from __future__ import annotations

import logging

from django.apps import AppConfig

logger = logging.getLogger("django_cfg.analytics")


class AnalyticsAppConfig(AppConfig):
    """
    First-party, self-hosted analytics.

    Provides:
    - Pageview / custom event ingest (synchronous; no worker, no daemon)
    - Cookieless sessions and visitor identity
    - Authenticated-user attribution (the thing Plausible/Umami cannot do)
    """

    name = "django_cfg.apps.tools.analytics"
    label = "cfg_analytics"
    verbose_name = "Analytics"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self) -> None:
        self._warn_on_unshared_cache()

    def _warn_on_unshared_cache(self) -> None:
        """Ingest stays *correct* on LocMemCache — but the operator should know.

        Identity is a stateless hash precisely so that a missing shared cache
        cannot corrupt data (see services/identity.py). The cost of not having
        one is only that every event re-computes the hash instead of hitting a
        cache, so this is a hint, not an error.
        """
        try:
            from django.conf import settings

            backend = settings.CACHES.get("default", {}).get("BACKEND", "")
            if "locmem" in backend.lower():
                logger.debug(
                    "Analytics: LocMemCache detected. Ingest is still correct "
                    "(identity is stateless), but a shared cache (Redis) would "
                    "let it skip the per-event hash."
                )
        except Exception:  # pragma: no cover - never break startup
            pass
