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

    This dataclass is used internally by the module. Configuration can come from:
    1. DjangoConfig.storage (preferred) - via get_current_config()
    2. Django settings.DJANGO_STORAGE (fallback)
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
        return cls(
            auto_cleanup=config.auto_cleanup,
            delete_on_replace=config.delete_on_replace,
            exclude_models=set(config.exclude_models),
            exclude_fields=set(config.exclude_fields),
            log_deletions=config.log_deletions,
            check_shared_files=config.check_shared_files,
            respect_soft_delete=config.respect_soft_delete,
            soft_delete_fields=set(config.soft_delete_fields),
        )

    @classmethod
    def from_django_settings(cls) -> "StorageCleanupConfig":
        """
        Load configuration from Django settings (fallback).

        Reads from settings.DJANGO_STORAGE dict.
        """
        from django.conf import settings

        config_dict = getattr(settings, "DJANGO_STORAGE", {})
        valid_fields = {f for f in cls.__dataclass_fields__}
        filtered_config = {k: v for k, v in config_dict.items() if k in valid_fields}
        return cls(**filtered_config)


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

    Priority:
    1. DjangoConfig.storage (via get_current_config)
    2. Django settings.DJANGO_STORAGE
    3. Default values
    """
    # Try DjangoConfig first
    config = _get_config_from_django_cfg()
    if config:
        return config

    # Fall back to Django settings
    return StorageCleanupConfig.from_django_settings()


def clear_config_cache() -> None:
    """Clear the configuration cache. Useful for testing."""
    get_config.cache_clear()
