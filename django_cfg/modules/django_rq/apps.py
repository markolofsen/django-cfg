"""django_rq — Django AppConfig."""

from __future__ import annotations

from django.apps import AppConfig


class DjangoRQMetricsConfig(AppConfig):
    name = "django_cfg.modules.django_rq"
    label = "django_rq_metrics"
    verbose_name = "RQ"
    default_auto_field = "django.db.models.BigAutoField"
