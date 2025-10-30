from django.apps import AppConfig


class DjangoImportExportConfig(AppConfig):
    """Django Import/Export integration app configuration."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_cfg.modules.django_import_export'
    label = 'django_cfg_import_export'
    verbose_name = 'Django Import/Export Integration'

    def ready(self):
        """Initialize module classes when Django is ready."""
        # Import and setup classes here to avoid AppRegistryNotReady
        from . import _setup_classes
        _setup_classes()
