"""
Core cleanup logic for Django Storage module.

Provides functions to identify and delete files associated with model instances.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, List, Optional, Tuple, Type

from django.db.models.fields.files import FieldFile, FileField

if TYPE_CHECKING:
    from django.db.models import Model

    from .config import StorageCleanupConfig

logger = logging.getLogger(__name__)


def get_file_fields(model: Type[Model]) -> List[Tuple[str, FileField]]:
    """
    Get all FileField/ImageField instances from a model.

    Args:
        model: The Django model class

    Returns:
        List of (field_name, field_instance) tuples
    """
    file_fields = []
    for model_field in model._meta.get_fields():
        if isinstance(model_field, FileField):
            file_fields.append((model_field.name, model_field))
    return file_fields


def is_model_excluded(model: Type[Model], config: StorageCleanupConfig) -> bool:
    """
    Check if model is excluded from cleanup.

    Args:
        model: The Django model class
        config: Cleanup configuration

    Returns:
        True if model should be excluded from cleanup
    """
    model_label = f"{model._meta.app_label}.{model._meta.object_name}"
    return model_label in config.exclude_models


def is_field_excluded(
    model: Type[Model],
    field_name: str,
    config: StorageCleanupConfig,
) -> bool:
    """
    Check if specific field is excluded from cleanup.

    Args:
        model: The Django model class
        field_name: Name of the field
        config: Cleanup configuration

    Returns:
        True if field should be excluded from cleanup
    """
    field_label = f"{model._meta.app_label}.{model._meta.object_name}.{field_name}"
    return field_label in config.exclude_fields


def has_soft_delete(model: Type[Model], config: StorageCleanupConfig) -> bool:
    """
    Check if model uses soft-delete pattern.

    Args:
        model: The Django model class
        config: Cleanup configuration

    Returns:
        True if model has any soft-delete indicator fields
    """
    model_fields = {f.name for f in model._meta.get_fields()}
    return bool(model_fields & config.soft_delete_fields)


def is_soft_deleted(instance: Model, config: StorageCleanupConfig) -> bool:
    """
    Check if instance is soft-deleted.

    Args:
        instance: The model instance
        config: Cleanup configuration

    Returns:
        True if instance appears to be soft-deleted
    """
    for field_name in config.soft_delete_fields:
        if hasattr(instance, field_name):
            value = getattr(instance, field_name)
            if value:  # deleted_at is not None, is_deleted is True, etc.
                return True
    return False


def delete_file(file_field: FieldFile, save: bool = False) -> bool:
    """
    Safely delete a file from storage.

    Args:
        file_field: The FieldFile instance to delete
        save: Whether to save the model after deletion

    Returns:
        True if file was deleted, False otherwise
    """
    if not file_field:
        return False

    try:
        file_name = file_field.name
        file_field.delete(save=save)
        logger.debug(f"Deleted file: {file_name}")
        return True
    except Exception as e:
        logger.error(f"Failed to delete file {file_field.name}: {e}")
        return False


def delete_file_by_name(
    storage,  # noqa: ANN001
    file_name: str,
    log_deletions: bool = False,
) -> bool:
    """
    Delete a file from storage by name.

    Args:
        storage: Django storage instance
        file_name: Path/name of the file to delete
        log_deletions: Whether to log the deletion

    Returns:
        True if file was deleted, False otherwise
    """
    if not file_name:
        return False

    try:
        if storage.exists(file_name):
            storage.delete(file_name)
            if log_deletions:
                logger.info(f"Deleted file: {file_name}")
            else:
                logger.debug(f"Deleted file: {file_name}")
            return True
        return False
    except Exception as e:
        logger.error(f"Failed to delete file {file_name}: {e}")
        return False


def is_file_shared(
    model: Type[Model],
    field_name: str,
    file_name: str,
    exclude_pk: Optional[int] = None,
) -> bool:
    """
    Check if the same file is used by other model instances.

    Args:
        model: The model class
        field_name: Name of the file field
        file_name: The file path/name to check
        exclude_pk: PK to exclude from check (current instance)

    Returns:
        True if file is used by other instances
    """
    if not file_name:
        return False

    queryset = model.objects.filter(**{field_name: file_name})
    if exclude_pk is not None:
        queryset = queryset.exclude(pk=exclude_pk)
    return queryset.exists()


def cleanup_instance_files(
    instance: Model,
    config: StorageCleanupConfig,
    fields_to_clean: Optional[List[str]] = None,
) -> int:
    """
    Delete all files associated with a model instance.

    Args:
        instance: The model instance
        config: Cleanup configuration
        fields_to_clean: Specific fields to clean (None = all)

    Returns:
        Number of files deleted
    """
    model = type(instance)

    if is_model_excluded(model, config):
        return 0

    deleted_count = 0
    file_fields = get_file_fields(model)

    for field_name, _field in file_fields:
        if fields_to_clean and field_name not in fields_to_clean:
            continue

        if is_field_excluded(model, field_name, config):
            continue

        file_field = getattr(instance, field_name)
        if not file_field:
            continue

        # Check if file is shared
        if config.check_shared_files:
            if is_file_shared(model, field_name, file_field.name, instance.pk):
                logger.debug(
                    f"Skipping shared file: {file_field.name} "
                    f"(used by other {model.__name__} instances)"
                )
                continue

        if delete_file(file_field, save=False):
            deleted_count += 1
            if config.log_deletions:
                logger.info(
                    f"Cleaned up file '{file_field.name}' "
                    f"from {model.__name__}(pk={instance.pk}).{field_name}"
                )

    return deleted_count
