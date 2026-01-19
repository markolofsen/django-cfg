"""
Storage configuration model for automatic file cleanup.
"""

from typing import Set

from pydantic import BaseModel, Field


class StorageConfig(BaseModel):
    """
    Storage cleanup configuration for automatic file deletion.

    Provides automatic file cleanup for FileField and ImageField when:
    - Model instances are deleted
    - File fields are updated with new files

    Example:
        ```python
        from django_cfg import DjangoConfig, StorageConfig

        class MyConfig(DjangoConfig):
            storage = StorageConfig(
                log_deletions=True,
                exclude_models=["backups.DatabaseBackup"],
            )
        ```
    """

    enabled: bool = Field(
        default=True,
        description="Enable storage cleanup module",
    )

    auto_cleanup: bool = Field(
        default=True,
        description="Enable automatic cleanup via signals for all models with FileField/ImageField",
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

    def __init__(self, **data):
        """Convert lists to sets if needed."""
        for field_name in ("exclude_models", "exclude_fields", "soft_delete_fields"):
            if field_name in data and isinstance(data[field_name], list):
                data[field_name] = set(data[field_name])
        super().__init__(**data)


__all__ = ["StorageConfig"]
