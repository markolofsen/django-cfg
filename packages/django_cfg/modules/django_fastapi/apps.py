"""Django app configuration for django_fastapi module."""

from django.apps import AppConfig


class DjangoFastAPIConfig(AppConfig):
    """
    FastAPI ORM Generator module.

    Provides:
    - Django model to SQLModel conversion
    - Pydantic schema generation
    - Async CRUD repository generation
    - Alembic migration support
    """

    name = "django_cfg.modules.django_fastapi"
    label = "cfg_fastapi"
    verbose_name = "FastAPI ORM Generator"
    default_auto_field = "django.db.models.BigAutoField"
