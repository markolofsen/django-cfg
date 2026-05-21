"""Django app configuration for the LLM module."""

from django.apps import AppConfig


class DjangoLLMConfig(AppConfig):
    """App config for django_llm.

    Registered as a Django app so its management commands (e.g.
    ``check_llm_balance``) are discoverable. The module itself defines no
    Django ORM models.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "django_cfg.modules.django_llm"
    verbose_name = "Django LLM"
