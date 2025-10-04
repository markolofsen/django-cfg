from django.apps import AppConfig


class SupportConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_cfg.apps.support'
    label = 'django_cfg_support'
    verbose_name = 'Django CFG Support'

    def ready(self):
        import django_cfg.apps.support.signals
