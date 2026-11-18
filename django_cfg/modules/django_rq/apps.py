"""django_rq — Django AppConfig."""

from __future__ import annotations

from django.apps import AppConfig


class DjangoRQMetricsConfig(AppConfig):
    name = "django_cfg.modules.django_rq"
    label = "django_rq_metrics"
    verbose_name = "RQ"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self) -> None:
        # Request id from the enqueuing request into the job's log lines.
        from django_cfg.modules.django_logging.rq_hooks import install

        install()
