"""
Django Cleanup Module.

Provides automatic file cleanup for FileField and ImageField when:
- Model instances are deleted
- File fields are updated with new files

Usage:
    # Automatic - enabled by default via DjangoConfig
    # Configure in your config.py:
    class MyConfig(DjangoConfig):
        storage = StorageConfig(
            log_deletions=True,
            exclude_models=["backups.DatabaseBackup"],
        )

    # Or disable:
    class MyConfig(DjangoConfig):
        storage = StorageConfig(enabled=False)

    # Manual (mixin) - for fine-grained control:
    from django_cfg.modules.django_cleanup import FileCleanupMixin

    class MyModel(FileCleanupMixin, models.Model):
        document = models.FileField(upload_to='docs/')

Example with exclusions:
    storage = StorageConfig(
        auto_cleanup=True,
        exclude_models=["backups.DatabaseBackup"],
        exclude_fields=["documents.Contract.original_scan"],
    )
"""

from .cleanup import (
    cleanup_instance_files,
    delete_file,
    delete_file_by_name,
    get_file_fields,
    has_soft_delete,
    is_file_shared,
    is_model_excluded,
    is_soft_deleted,
)
from .config import StorageCleanupConfig, clear_config_cache, get_config
from .signals import connect_signals_for_model, disconnect_signals_for_model


def __getattr__(name: str):
    """Lazy import for mixins to avoid AppRegistryNotReady error."""
    if name == "FileCleanupMixin":
        from .mixins import FileCleanupMixin
        return FileCleanupMixin
    if name == "FileCleanupQuerySet":
        from .mixins import FileCleanupQuerySet
        return FileCleanupQuerySet
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    # Config
    "StorageCleanupConfig",
    "get_config",
    "clear_config_cache",
    # Cleanup functions
    "cleanup_instance_files",
    "delete_file",
    "delete_file_by_name",
    "get_file_fields",
    "is_file_shared",
    "is_model_excluded",
    "has_soft_delete",
    "is_soft_deleted",
    # Mixins (lazy loaded)
    "FileCleanupMixin",
    "FileCleanupQuerySet",
    # Signal management
    "connect_signals_for_model",
    "disconnect_signals_for_model",
]

default_app_config = "django_cfg.modules.django_cleanup.apps.DjangoCleanupConfig"
