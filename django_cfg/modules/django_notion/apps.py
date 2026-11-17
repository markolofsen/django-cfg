"""django_notion: mirror leads into Notion."""

from django.apps import AppConfig


class DjangoNotionConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_cfg.modules.django_notion"
    label = "django_cfg_notion"
    verbose_name = "Notion"
