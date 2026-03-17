"""
django_rq — Django AppConfig.

Connects RQ lifecycle capture hooks at startup if django_cf is ready.
"""

from __future__ import annotations

import logging

from django.apps import AppConfig

logger = logging.getLogger("django_cfg.django_rq")


class DjangoRQMetricsConfig(AppConfig):
    name = "django_cfg.modules.django_rq"
    label = "django_rq_metrics"
    verbose_name = "RQ Metrics (D1)"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self) -> None:
        try:
            from .capture import connect_rq_hooks
            connect_rq_hooks()
        except Exception as exc:
            logger.warning("django_rq: failed to connect capture hooks — %s", exc)
