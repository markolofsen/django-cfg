"""Django app configuration for LLM monitoring module."""

from django.apps import AppConfig


class DjangoLLMMonitoringConfig(AppConfig):
    """App config for LLM balance monitoring."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "django_cfg.modules.django_llm_monitoring"
    verbose_name = "LLM Balance Monitoring"
