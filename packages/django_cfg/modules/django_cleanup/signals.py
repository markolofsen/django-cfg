"""
Django signal handlers for automatic file cleanup.

Handles:
- post_delete: Clean up files when model instances are deleted
- pre_save/post_save: Clean up old files when file fields are updated
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Dict, Type

from django.db import transaction
from django.db.models.signals import post_delete, post_save, pre_save

if TYPE_CHECKING:
    from django.db.models import Model

from .cleanup import (
    cleanup_instance_files,
    delete_file_by_name,
    get_file_fields,
    has_soft_delete,
    is_field_excluded,
    is_model_excluded,
    is_soft_deleted,
)
from .config import StorageCleanupConfig, get_config

logger = logging.getLogger(__name__)

# Cache for tracking original file values before save
_original_files_cache: Dict[str, Dict[str, str | None]] = {}


def _get_cache_key(instance: Model) -> str:
    """Generate cache key for instance."""
    return f"{type(instance).__name__}:{instance.pk}"


def _cache_original_files(instance: Model) -> None:
    """Store original file values before save."""
    if not instance.pk:
        return

    model = type(instance)
    file_fields = get_file_fields(model)

    if not file_fields:
        return

    try:
        original = model.objects.get(pk=instance.pk)
        cache_key = _get_cache_key(instance)
        _original_files_cache[cache_key] = {
            field_name: getattr(original, field_name).name
            if getattr(original, field_name)
            else None
            for field_name, _ in file_fields
        }
    except model.DoesNotExist:
        pass


def _get_original_file(instance: Model, field_name: str) -> str | None:
    """Get original file name from cache."""
    cache_key = _get_cache_key(instance)
    cached = _original_files_cache.get(cache_key, {})
    return cached.get(field_name)


def _clear_cache(instance: Model) -> None:
    """Clear cached original files for instance."""
    cache_key = _get_cache_key(instance)
    _original_files_cache.pop(cache_key, None)


def file_cleanup_pre_save(
    sender: Type[Model],
    instance: Model,
    **kwargs: Any,
) -> None:
    """
    Pre-save signal handler to track file changes.

    Caches original file values for comparison after save.
    """
    config = get_config()

    if not config.auto_cleanup or not config.delete_on_replace:
        return

    if is_model_excluded(sender, config):
        return

    # Cache original values for comparison after save
    _cache_original_files(instance)


def file_cleanup_post_save(
    sender: Type[Model],
    instance: Model,
    created: bool,
    **kwargs: Any,
) -> None:
    """
    Post-save signal handler to delete replaced files.

    Compares current file values with cached originals and deletes old files.
    """
    if created:
        _clear_cache(instance)
        return

    config = get_config()

    if not config.auto_cleanup or not config.delete_on_replace:
        _clear_cache(instance)
        return

    if is_model_excluded(sender, config):
        _clear_cache(instance)
        return

    file_fields = get_file_fields(sender)

    for field_name, field in file_fields:
        if is_field_excluded(sender, field_name, config):
            continue

        original_name = _get_original_file(instance, field_name)
        current_file = getattr(instance, field_name)
        current_name = current_file.name if current_file else None

        # File was replaced (different file) or cleared
        if original_name and original_name != current_name:
            # Capture values for closure
            old_name = original_name
            storage = field.storage
            log_deletions = config.log_deletions

            # Delete old file using transaction.on_commit for safety
            def delete_old_file(
                name: str = old_name,
                stg: Any = storage,
                log: bool = log_deletions,
            ) -> None:
                delete_file_by_name(stg, name, log)

            transaction.on_commit(delete_old_file)

    # Clear cache
    _clear_cache(instance)


def file_cleanup_post_delete(
    sender: Type[Model],
    instance: Model,
    **kwargs: Any,
) -> None:
    """
    Post-delete signal handler to cleanup files.

    Deletes all files associated with the deleted instance.
    """
    config = get_config()

    if not config.auto_cleanup:
        return

    if is_model_excluded(sender, config):
        return

    # Check soft-delete - if instance was soft-deleted, don't delete files
    if config.respect_soft_delete and has_soft_delete(sender, config):
        if is_soft_deleted(instance, config):
            logger.debug(
                f"Skipping file cleanup for soft-deleted "
                f"{sender.__name__}(pk={instance.pk})"
            )
            return

    # Capture instance data for closure
    # We need to collect file info before the transaction commits
    # because the instance might be garbage collected
    files_to_delete = []
    file_fields = get_file_fields(sender)

    for field_name, field in file_fields:
        if is_field_excluded(sender, field_name, config):
            continue

        file_field = getattr(instance, field_name)
        if file_field and file_field.name:
            files_to_delete.append((field.storage, file_field.name))

    if not files_to_delete:
        return

    log_deletions = config.log_deletions

    # Use transaction.on_commit for safety
    def cleanup() -> None:
        for storage, file_name in files_to_delete:
            delete_file_by_name(storage, file_name, log_deletions)

    transaction.on_commit(cleanup)


def connect_signals_for_model(model: Type[Model]) -> None:
    """
    Connect cleanup signals to a specific model.

    Args:
        model: The Django model class to connect signals to
    """
    file_fields = get_file_fields(model)

    if not file_fields:
        return

    config = get_config()

    if is_model_excluded(model, config):
        return

    model_label = model._meta.label

    # Connect pre_save for tracking file changes
    pre_save.connect(
        file_cleanup_pre_save,
        sender=model,
        dispatch_uid=f"storage_cleanup_pre_save_{model_label}",
    )

    # Connect post_save for deleting replaced files
    post_save.connect(
        file_cleanup_post_save,
        sender=model,
        dispatch_uid=f"storage_cleanup_post_save_{model_label}",
    )

    # Connect post_delete for deleting files on instance deletion
    post_delete.connect(
        file_cleanup_post_delete,
        sender=model,
        dispatch_uid=f"storage_cleanup_post_delete_{model_label}",
    )

    logger.debug(f"Connected file cleanup signals for {model_label}")


def disconnect_signals_for_model(model: Type[Model]) -> None:
    """
    Disconnect cleanup signals from a specific model.

    Args:
        model: The Django model class to disconnect signals from
    """
    model_label = model._meta.label

    pre_save.disconnect(
        dispatch_uid=f"storage_cleanup_pre_save_{model_label}",
    )
    post_save.disconnect(
        dispatch_uid=f"storage_cleanup_post_save_{model_label}",
    )
    post_delete.disconnect(
        dispatch_uid=f"storage_cleanup_post_delete_{model_label}",
    )

    logger.debug(f"Disconnected file cleanup signals for {model_label}")
