"""
Terminal app configuration.
"""

from django.apps import AppConfig


class TerminalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.terminal'
    verbose_name = 'Web Terminal'

    def ready(self):
        """Register Centrifugo RPC handlers on startup."""
        try:
            from . import centrifugo_handlers  # noqa: F401
        except ImportError:
            pass
