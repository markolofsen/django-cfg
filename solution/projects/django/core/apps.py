from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'Core'

    def ready(self):
        """Initialize core app."""
        # Import Centrifugo RPC handlers to register them
        try:
            from . import centrifugo_handlers
        except ImportError:
            pass
