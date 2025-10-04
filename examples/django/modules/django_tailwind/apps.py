from django.apps import AppConfig


class DjangoTailwindConfig(AppConfig):
    """Django Tailwind Layouts app configuration."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_cfg.modules.django_tailwind'
    label = 'django_cfg_tailwind'
    verbose_name = 'Django Tailwind Layouts'
