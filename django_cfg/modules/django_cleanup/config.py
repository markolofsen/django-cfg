"""
Configuration for Django Storage Cleanup module.

Loads configuration from DjangoConfig.storage or falls back to Django settings.
"""

from dataclasses import dataclass, field
from functools import lru_cache
from typing import TYPE_CHECKING, Optional, Set

if TYPE_CHECKING:
    from django_cfg.models.django.storage import StorageConfig as PydanticStorageConfig


@dataclass
class StorageCleanupConfig:
    """
    Runtime configuration for file cleanup behavior.

    Used internally by the module. Values come from `DjangoConfig.storage`
    via `get_current_config()`; defaults apply when no config is loaded.
    """

    # Enable automatic cleanup for all models
    auto_cleanup: bool = True

    # Delete old file when field value changes
    delete_on_replace: bool = True

    # Models to exclude from auto-cleanup (app_label.ModelName)
    exclude_models: Set[str] = field(default_factory=set)

    # Specific fields to exclude (app_label.ModelName.field_name)
    exclude_fields: Set[str] = field(default_factory=set)

    # Log file deletions
    log_deletions: bool = False

    # Check if file is used by other records before deleting
    check_shared_files: bool = False

    # Respect soft-delete (don't delete files for soft-deleted records)
    respect_soft_delete: bool = True

    # Soft-delete field names to check
    soft_delete_fields: Set[str] = field(
        default_factory=lambda: {"deleted_at", "is_deleted", "deleted"}
    )

    def __post_init__(self) -> None:
        """Convert lists to sets if needed."""
        if isinstance(self.exclude_models, list):
            self.exclude_models = set(self.exclude_models)
        if isinstance(self.exclude_fields, list):
            self.exclude_fields = set(self.exclude_fields)
        if isinstance(self.soft_delete_fields, list):
            self.soft_delete_fields = set(self.soft_delete_fields)

    @classmethod
    def from_pydantic_config(
        cls, config: "PydanticStorageConfig"
    ) -> "StorageCleanupConfig":
        """
        Create from Pydantic StorageConfig model.

        Args:
            config: StorageConfig from DjangoConfig.storage

        Returns:
            StorageCleanupConfig instance
        """
        cleanup = config.cleanup
        return cls(
            auto_cleanup=cleanup.auto_cleanup,
            delete_on_replace=cleanup.delete_on_replace,
            exclude_models=set(cleanup.exclude_models),
            exclude_fields=set(cleanup.exclude_fields),
            log_deletions=cleanup.log_deletions,
            check_shared_files=cleanup.check_shared_files,
            respect_soft_delete=cleanup.respect_soft_delete,
            soft_delete_fields=set(cleanup.soft_delete_fields),
        )


def _get_config_from_django_cfg() -> Optional[StorageCleanupConfig]:
    """
    Try to get config from DjangoConfig.storage.

    Returns:
        StorageCleanupConfig if DjangoConfig is available and has storage config,
        None otherwise.
    """
    try:
        from django_cfg.core.state import get_current_config

        django_config = get_current_config()
        if django_config and django_config.storage:
            return StorageCleanupConfig.from_pydantic_config(django_config.storage)
    except Exception:
        pass
    return None


@lru_cache(maxsize=1)
def get_config() -> StorageCleanupConfig:
    """
    Get cached configuration instance.

    Reads `DjangoConfig.storage`; falls back to dataclass defaults when no
    config is loaded (e.g. plain-Django test setups).
    """
    return _get_config_from_django_cfg() or StorageCleanupConfig()


def is_enabled() -> bool:
    """
    Whether the cleanup module is enabled (`DjangoConfig.storage.enabled`).

    Defaults to True when no config is loaded, matching StorageConfig's default.
    """
    try:
        from django_cfg.core.state import get_current_config

        django_config = get_current_config()
        if django_config and django_config.storage is not None:
            return django_config.storage.enabled
    except Exception:
        pass
    return True


def clear_config_cache() -> None:
    """Clear the configuration cache. Useful for testing."""
    get_config.cache_clear()
