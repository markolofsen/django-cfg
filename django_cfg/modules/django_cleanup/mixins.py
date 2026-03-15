"""
Model mixins for explicit file cleanup control.

Use these mixins when you need fine-grained control over file cleanup,
or when auto_cleanup is disabled globally.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, List, Optional

from django.db import models

from .cleanup import cleanup_instance_files, delete_file, get_file_fields
from .config import get_config

if TYPE_CHECKING:
    from django.db.models import QuerySet


class FileCleanupMixin(models.Model):
    """
    Mixin for explicit file cleanup control.

    Use this when you need fine-grained control over file cleanup,
    or when auto_cleanup is disabled.

    Example:
        class MyModel(FileCleanupMixin, models.Model):
            document = models.FileField(upload_to='documents/')
            image = models.ImageField(upload_to='images/')

            # Optional: exclude specific fields from cleanup
            file_cleanup_exclude_fields = ['backup_document']
    """

    class Meta:
        abstract = True

    # Override to exclude specific fields from cleanup
    file_cleanup_exclude_fields: ClassVar[List[str]] = []

    def delete(
        self,
        using: Optional[str] = None,
        keep_parents: bool = False,
    ) -> tuple:
        """Override delete to cleanup files before deletion."""
        config = get_config()

        # Get fields to clean (exclude specified)
        file_fields = get_file_fields(type(self))
        fields_to_clean = [
            name
            for name, _ in file_fields
            if name not in self.file_cleanup_exclude_fields
        ]

        # Cleanup files before delete
        cleanup_instance_files(self, config, fields_to_clean)

        return super().delete(using=using, keep_parents=keep_parents)

    def save(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
        """Override save to cleanup replaced files."""
        if self.pk:
            self._cleanup_replaced_files()
        return super().save(*args, **kwargs)

    def _cleanup_replaced_files(self) -> None:
        """Delete old files when field values change."""
        model = type(self)
        config = get_config()

        if not config.delete_on_replace:
            return

        try:
            original = model.objects.get(pk=self.pk)
        except model.DoesNotExist:
            return

        file_fields = get_file_fields(model)

        for field_name, _field in file_fields:
            if field_name in self.file_cleanup_exclude_fields:
                continue

            original_file = getattr(original, field_name)
            current_file = getattr(self, field_name)

            original_name = original_file.name if original_file else None
            current_name = current_file.name if current_file else None

            if original_name and original_name != current_name:
                delete_file(original_file)

    def cleanup_file(self, field_name: str) -> bool:
        """
        Manually cleanup a specific file field.

        Args:
            field_name: Name of the file field to cleanup

        Returns:
            True if file was deleted
        """
        file_field = getattr(self, field_name, None)
        if file_field:
            return delete_file(file_field, save=False)
        return False

    def cleanup_all_files(self) -> int:
        """
        Manually cleanup all file fields.

        Returns:
            Number of files deleted
        """
        config = get_config()
        return cleanup_instance_files(self, config)


class FileCleanupQuerySet(models.QuerySet):
    """
    QuerySet that cleans up files on bulk delete.

    Note: This is more expensive than regular delete as it needs
    to fetch instances first to get file references.

    Usage:
        class MyModel(models.Model):
            file = models.FileField(upload_to='files/')

            objects = FileCleanupQuerySet.as_manager()
    """

    def delete(self) -> tuple:
        """Override delete to cleanup files for all instances."""
        config = get_config()

        # Collect all files to delete
        files_to_delete = []

        for instance in self.iterator():
            file_fields = get_file_fields(type(instance))
            for field_name, field in file_fields:
                file_field = getattr(instance, field_name)
                if file_field and file_field.name:
                    files_to_delete.append((field.storage, file_field.name))

        # Perform the delete
        result = super().delete()

        # Now delete the files
        from .cleanup import delete_file_by_name

        for storage, file_name in files_to_delete:
            delete_file_by_name(storage, file_name, config.log_deletions)

        return result
