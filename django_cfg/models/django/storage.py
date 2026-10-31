"""
Storage configuration: file cleanup behavior and (later) storage backends.

`StorageConfig` is a container. `FileCleanupConfig` owns the cleanup fields
that used to live directly on it; the flat form is still accepted and mapped
onto `cleanup` with a DeprecationWarning.
"""

import warnings
from typing import Any, Dict, List, Literal, Optional, Set

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

    outbox: bool = Field(
        default=False,
        description="Record deletions in the StorageDeletion table inside the transaction and "
        "let a worker delete the files (retries, backoff, CDN purge). Needed for "
        "`register_owned_files`. Off keeps the direct on-commit delete of FileField files.",
    )

    mode: Literal["delete", "queue_only"] = Field(
        default="delete",
        description="`delete`: this project's worker deletes the files. `queue_only`: rows are "
        "written but nothing is deleted here; another service owns the files and drains the table.",
    )

    allowed_prefixes: List[str] = Field(
        default_factory=list,
        description="Key prefixes the outbox may delete under, e.g. ['films/', 'avatars/']. A key "
        "outside them is refused. Without any, only exact FileField keys are deleted; "
        "prefix deletions are refused.",
    )

    dry_run: bool = Field(
        default=False,
        description="The worker logs what it would delete and changes nothing",
    )

    max_attempts: int = Field(default=8, ge=1, description="Attempts before a row is marked failed")
    backoff_seconds: int = Field(default=30, ge=1, description="Base of the exponential retry delay")
    batch_size: int = Field(default=200, ge=1, description="Outbox rows taken per worker run")
    schedule_interval: int = Field(
        default=60, ge=0, description="Seconds between scheduled worker runs (0 = no schedule); needs django_rq"
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


class CDNPurgeConfig(BaseModel):
    """
    Cloudflare cache purge by URL, run after a file is deleted from storage.

    The token and zone id are read from the environment when the worker runs,
    never stored in code. Without a token the purge is skipped and counted.

    Example:
        ```python
        StorageConfig(cdn=CDNPurgeConfig(base_url="https://cdn.example.com"))
        ```
    """

    provider: Literal["cloudflare"] = "cloudflare"
    base_url: Optional[str] = Field(
        default=None,
        description="Public origin the files are served from; defaults to https://<backend.custom_domain>",
    )
    zone_id_env: str = Field(default="CLOUDFLARE_ZONE_ID", description="Env var holding the zone id")
    api_token_env: str = Field(default="CLOUDFLARE_API_TOKEN", description="Env var holding the API token")
    batch_size: int = Field(default=30, ge=1, le=100, description="URLs per purge request (Cloudflare's per-call limit)")
    timeout: int = Field(default=15, ge=1, description="Seconds per request")


class StorageConfig(BaseModel):
    """
    Storage configuration.

    Groups file-storage concerns that are configured independently:

    - `cleanup` — automatic deletion of orphaned files (see `FileCleanupConfig`).
    - `backend` — where media is stored in production. `None` keeps Django's
      local filesystem storage (see `S3StorageConfig`). Development and test
      always write and delete on local disk; with a `custom_domain`, `url()`
      of a file missing locally points at the remote copy (read-only).

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
        description="Object storage for media in production; None uses local "
        "filesystem storage. Development and test always write and delete on "
        "local disk; only url() of a file missing locally falls back to the "
        "backend's custom_domain",
    )

    cdn: Optional[CDNPurgeConfig] = Field(
        default=None,
        description="Purge these URLs from the CDN after their files are deleted (outbox worker)",
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

    def get_rq_schedules(self) -> list:
        """The outbox worker's schedule; empty unless the outbox runs deletions here."""
        cleanup = self.cleanup
        if not (self.enabled and cleanup.outbox and cleanup.mode == "delete" and cleanup.schedule_interval):
            return []

        from django_cfg.models.django.django_rq import RQScheduleConfig

        return [
            RQScheduleConfig(
                func="django_cfg.modules.django_cleanup.sync.tasks.drain_storage_outbox",
                interval=cleanup.schedule_interval,
                timeout=900,
                queue="default",
                description=f"Delete files queued by the storage outbox (every {cleanup.schedule_interval}s)",
            )
        ]

    def effective_backend(self, *, production: bool) -> Optional[S3StorageConfig]:
        """
        Backend actually in use: `backend` in production, None elsewhere.

        A dev or test run must never reach the bucket: uploads would land next
        to production objects, and cleanup signals would delete them.
        """
        return self.backend if production else None

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


__all__ = ["StorageConfig", "FileCleanupConfig", "CDNPurgeConfig", "S3StorageConfig"]
