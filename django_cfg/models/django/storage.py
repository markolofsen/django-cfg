"""
Storage configuration: file cleanup behavior and (later) storage backends.

`StorageConfig` is a container. `FileCleanupConfig` owns the cleanup fields
that used to live directly on it; the flat form is still accepted and mapped
onto `cleanup` with a DeprecationWarning.
"""

import warnings
from typing import Any, Dict, Optional, Set

from pydantic import BaseModel, Field, model_validator

from .storage_backend import S3StorageConfig

# Cleanup fields as they appeared on the flat StorageConfig. Used to detect and
# migrate the legacy form.
_CLEANUP_FIELDS = frozenset(
    {
        "auto_cleanup",
        "delete_on_replace",
        "exclude_models",
        "exclude_fields",
        "log_deletions",
        "check_shared_files",
        "respect_soft_delete",
        "soft_delete_fields",
    }
)

_SET_FIELDS = ("exclude_models", "exclude_fields", "soft_delete_fields")


class FileCleanupConfig(BaseModel):
    """
    Automatic file deletion for FileField and ImageField.

    Deletes the underlying file when a model instance is deleted, or when a
    file field is replaced with a new file.

    Example:
        ```python
        from django_cfg import DjangoConfig, StorageConfig, FileCleanupConfig

        class MyConfig(DjangoConfig):
            storage = StorageConfig(
                cleanup=FileCleanupConfig(
                    log_deletions=True,
                    exclude_models=["backups.DatabaseBackup"],
                )
            )
        ```
    """

    auto_cleanup: bool = Field(
        default=True,
        description="Register cleanup signals for all models with FileField/ImageField",
    )

    delete_on_replace: bool = Field(
        default=True,
        description="Delete old file when field value changes to a new file",
    )

    exclude_models: Set[str] = Field(
        default_factory=set,
        description="Models to exclude from auto-cleanup (e.g., 'backups.DatabaseBackup')",
    )

    exclude_fields: Set[str] = Field(
        default_factory=set,
        description="Specific fields to exclude (e.g., 'documents.Contract.original_scan')",
    )

    log_deletions: bool = Field(
        default=False,
        description="Log all file deletions (INFO level)",
    )

    check_shared_files: bool = Field(
        default=False,
        description="Check if file is used by other records before deleting. "
        "Warning: adds a DB query per file field.",
    )

    respect_soft_delete: bool = Field(
        default=True,
        description="Don't delete files for soft-deleted records (records with deleted_at, is_deleted, etc.)",
    )

    soft_delete_fields: Set[str] = Field(
        default_factory=lambda: {"deleted_at", "is_deleted", "deleted"},
        description="Field names that indicate soft-delete pattern",
    )

    @model_validator(mode="before")
    @classmethod
    def _coerce_sets(cls, data: Any) -> Any:
        """Accept lists for set-typed fields."""
        if isinstance(data, dict):
            for name in _SET_FIELDS:
                if isinstance(data.get(name), list):
                    data[name] = set(data[name])
        return data


class StorageConfig(BaseModel):
    """
    Storage configuration.

    Groups file-storage concerns that are configured independently:

    - `cleanup` — automatic deletion of orphaned files (see `FileCleanupConfig`).
    - `backend` — where media is stored. `None` keeps Django's local
      filesystem storage (see `S3StorageConfig`).

    Example:
        ```python
        from django_cfg import DjangoConfig, StorageConfig, FileCleanupConfig, S3StorageConfig

        class MyConfig(DjangoConfig):
            storage = StorageConfig(
                backend=S3StorageConfig.r2(account_id="…", bucket_name="media"),
                cleanup=FileCleanupConfig(log_deletions=True),
            )
        ```

    Setting `enabled=False` disables the cleanup app entirely: it is left out
    of INSTALLED_APPS and no signals are registered. It does not affect
    `backend`.
    """

    enabled: bool = Field(
        default=True,
        description="Enable the storage cleanup module (app registration + signals)",
    )

    cleanup: FileCleanupConfig = Field(
        default_factory=FileCleanupConfig,
        description="Automatic file cleanup behavior",
    )

    backend: Optional[S3StorageConfig] = Field(
        default=None,
        description="Object storage for media; None uses local filesystem storage",
    )

    @model_validator(mode="before")
    @classmethod
    def _migrate_flat_cleanup_fields(cls, data: Any) -> Any:
        """
        Accept the pre-2.4 flat form, where cleanup fields sat on StorageConfig.

        `StorageConfig(log_deletions=True)` still works and is folded into
        `cleanup`. Explicit `cleanup=` wins; flat keys alongside it are ignored
        rather than silently merged, since merging would make precedence
        depend on field order.
        """
        if not isinstance(data, dict):
            return data

        legacy = {k: data.pop(k) for k in list(data) if k in _CLEANUP_FIELDS}
        if not legacy:
            return data

        if "cleanup" in data:
            warnings.warn(
                "StorageConfig received both `cleanup=` and the deprecated flat "
                f"cleanup fields ({', '.join(sorted(legacy))}). The flat fields "
                "are ignored. Move them into FileCleanupConfig.",
                DeprecationWarning,
                stacklevel=3,
            )
            return data

        warnings.warn(
            "Passing cleanup fields directly to StorageConfig is deprecated "
            f"({', '.join(sorted(legacy))}). Use "
            "StorageConfig(cleanup=FileCleanupConfig(...)) instead.",
            DeprecationWarning,
            stacklevel=3,
        )
        data["cleanup"] = FileCleanupConfig(**legacy)
        return data

    def __getattr__(self, name: str) -> Any:
        """Read cleanup fields off the container, as the flat form allowed."""
        if name in _CLEANUP_FIELDS:
            return getattr(self.cleanup, name)
        raise AttributeError(
            f"{type(self).__name__!r} object has no attribute {name!r}"
        )

    def model_dump_legacy(self) -> Dict[str, Any]:
        """Flat dict of cleanup settings, for consumers reading the old shape."""
        return self.cleanup.model_dump()


__all__ = ["StorageConfig", "FileCleanupConfig", "S3StorageConfig"]
