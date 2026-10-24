from django.apps import AppConfig

from .__cfg__ import settings


class SupportConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'extensions.apps.support'
    label = settings.full_app_label  # Auto: cfg__support
    verbose_name = 'Support'

    def ready(self):
        pass
