"""
Database Backup Admin Interface.

Provides admin views for managing database backups and restores using
Django-CFG declarative AdminConfig pattern.
"""

from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import path, reverse

from django_cfg.modules.django_admin import (
    ActionConfig,
    AdminConfig,
    BadgeField,
    DateTimeField,
    FieldsetConfig,
    Icons,
    ShortUUIDField,
    TextField,
)
from django_cfg.modules.django_admin.base import PydanticAdmin

from .models import BackupRecord, RestoreRecord
from .services import BackupService


# =============================================================================
# Actions
# =============================================================================


def create_backup_action(modeladmin, request, queryset):
    """Admin action to create backups for selected database aliases."""
    databases = set(queryset.values_list("database_alias", flat=True))
    service = BackupService()

    success_count = 0
    for db in databases:
        try:
            record = service.create_backup(database_alias=db)
            if record.status == "completed":
                success_count += 1
        except Exception:
            pass

    messages.success(request, f"Created {success_count} backups")


def delete_backup_files(modeladmin, request, queryset):
    """Admin action to delete backup files (mark as deleted)."""
    from pathlib import Path

    count = 0
    for backup in queryset.filter(status="completed"):
        try:
            if backup.storage_backend == "local":
                path = Path(backup.file_path)
                if path.exists():
                    path.unlink()
            backup.mark_deleted()
            count += 1
        except Exception:
            pass

    messages.success(request, f"Deleted {count} backup files")


def create_new_backup(modeladmin, request):
    """Changelist action to create a new backup."""
    from django.conf import settings

    database = request.GET.get("database", "default")

    if database not in settings.DATABASES:
        messages.error(request, f"Database '{database}' not found")
        return redirect(reverse("admin:db_backup_backuprecord_changelist"))

    service = BackupService()

    try:
        record = service.create_backup(
            database_alias=database,
            is_scheduled=False,
            is_manual=True,
        )

        if record.status == "completed":
            messages.success(
                request,
                f"Backup created successfully: {record.filename} ({record.file_size_human})",
            )
        else:
            messages.error(request, f"Backup failed: {record.error_message}")

    except Exception as e:
        messages.error(request, f"Backup failed: {e}")

    return redirect(reverse("admin:db_backup_backuprecord_changelist"))


def cleanup_old_backups(modeladmin, request):
    """Changelist action to cleanup old backups."""
    service = BackupService()

    try:
        service.cleanup_old_backups()
        messages.success(request, "Old backups cleaned up successfully")
    except Exception as e:
        messages.error(request, f"Cleanup failed: {e}")

    return redirect(reverse("admin:db_backup_backuprecord_changelist"))


# =============================================================================
# BackupRecord Admin
# =============================================================================

backup_record_config = AdminConfig(
    model=BackupRecord,

    # List display
    list_display=[
        "id",
        "database_alias",
        "database_engine",
        "filename",
        "file_size",
        "status",
        "duration_seconds",
        "created_at",
        "is_scheduled",
    ],

    list_display_links=["id"],
    list_per_page=50,

    # Filters and search
    list_filter=[
        "status",
        "database_engine",
        "storage_backend",
        "is_scheduled",
        "is_manual",
        "created_at",
    ],

    search_fields=[
        "id",
        "database_alias",
        "database_name",
        "filename",
    ],

    # Ordering
    ordering=["-created_at"],

    # Display fields
    display_fields=[
        ShortUUIDField(
            name="id",
            title="ID",
            length=8,
        ),
        BadgeField(
            name="database_engine",
            title="Engine",
            label_map={
                "postgresql": "primary",
                "mysql": "info",
                "sqlite": "secondary",
            },
            icon=Icons.STORAGE,
        ),
        TextField(
            name="filename",
            title="Filename",
            truncate=50,
        ),
        BadgeField(
            name="status",
            title="Status",
            label_map={
                "pending": "warning",
                "running": "info",
                "completed": "success",
                "failed": "danger",
                "deleted": "secondary",
            },
            icon=Icons.INFO,
        ),
        DateTimeField(
            name="created_at",
            title="Created",
            show_relative=True,
            ordering="created_at",
        ),
        BadgeField(
            name="is_scheduled",
            title="Type",
            label_map={
                True: "info",
                False: "secondary",
            },
        ),
    ],

    # Fieldsets
    fieldsets=[
        FieldsetConfig(
            title="Backup Information",
            fields=["id", "database_alias", "database_name", "database_engine"],
        ),
        FieldsetConfig(
            title="File Details",
            fields=["filename", "file_path", "file_size", "compression", "checksum"],
        ),
        FieldsetConfig(
            title="Storage",
            fields=["storage_backend", "storage_bucket", "encrypted"],
        ),
        FieldsetConfig(
            title="Status",
            fields=["status", "error_message", "started_at", "completed_at", "duration_seconds"],
        ),
        FieldsetConfig(
            title="Statistics",
            fields=["tables_count", "rows_count", "is_scheduled", "is_manual"],
            collapsed=True,
        ),
        FieldsetConfig(
            title="Metadata",
            fields=["metadata", "created_at"],
            collapsed=True,
        ),
    ],

    # Readonly fields
    readonly_fields=[
        "id",
        "database_alias",
        "database_name",
        "database_engine",
        "filename",
        "file_path",
        "file_size",
        "compression",
        "encrypted",
        "storage_backend",
        "storage_bucket",
        "status",
        "error_message",
        "started_at",
        "completed_at",
        "duration_seconds",
        "created_at",
        "is_scheduled",
        "is_manual",
        "tables_count",
        "rows_count",
        "checksum",
        "metadata",
    ],

    # Actions
    actions=[
        ActionConfig(
            name="create_backup_action",
            description="Create backup for selected databases",
            variant="success",
            icon="backup",
            handler=create_backup_action,
        ),
        ActionConfig(
            name="delete_backup_files",
            description="Delete backup files (mark as deleted)",
            variant="danger",
            icon="delete",
            confirmation=True,
            handler=delete_backup_files,
        ),
        ActionConfig(
            name="create_new_backup",
            action_type="changelist",
            description="Create New Backup",
            variant="success",
            icon="add",
            handler=create_new_backup,
        ),
        ActionConfig(
            name="cleanup_old_backups",
            action_type="changelist",
            description="Cleanup Old Backups",
            variant="warning",
            icon="cleaning_services",
            confirmation=True,
            handler=cleanup_old_backups,
        ),
    ],
)


@admin.register(BackupRecord)
class BackupRecordAdmin(PydanticAdmin):
    """Admin interface for backup records."""

    config = backup_record_config

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<str:pk>/restore/",
                self.admin_site.admin_view(self.restore_backup_view),
                name="db_backup_restore",
            ),
        ]
        return custom_urls + urls

    def restore_backup_view(self, request, pk):
        """View to restore from backup."""
        try:
            backup = BackupRecord.objects.get(pk=pk)
        except BackupRecord.DoesNotExist:
            messages.error(request, "Backup not found")
            return HttpResponseRedirect(
                reverse("admin:db_backup_backuprecord_changelist")
            )

        if backup.status != "completed":
            messages.error(request, f"Cannot restore from backup with status: {backup.status}")
            return HttpResponseRedirect(
                reverse("admin:db_backup_backuprecord_changelist")
            )

        target = request.GET.get("target", backup.database_alias)

        service = BackupService()

        try:
            record = service.restore_backup(
                backup_id=str(backup.id),
                target_database_alias=target,
                created_by=request.user.username if request.user else "admin",
            )

            if record.status == "completed":
                messages.success(
                    request,
                    f"Database restored successfully from {backup.filename}",
                )
            else:
                messages.error(request, f"Restore failed: {record.error_message}")

        except Exception as e:
            messages.error(request, f"Restore failed: {e}")

        return HttpResponseRedirect(
            reverse("admin:db_backup_backuprecord_changelist")
        )

    def has_add_permission(self, request):
        """Disable add via form - use create_new_backup action instead."""
        return False


# =============================================================================
# RestoreRecord Admin
# =============================================================================

restore_record_config = AdminConfig(
    model=RestoreRecord,

    # List display
    list_display=[
        "id",
        "backup",
        "target_database_alias",
        "status",
        "duration_seconds",
        "created_by",
        "created_at",
    ],

    list_display_links=["id"],
    list_per_page=50,

    # Filters and search
    list_filter=[
        "status",
        "target_database_alias",
        "created_at",
    ],

    search_fields=[
        "id",
        "backup__filename",
        "target_database_alias",
        "created_by",
    ],

    # Ordering
    ordering=["-created_at"],

    # Display fields
    display_fields=[
        ShortUUIDField(
            name="id",
            title="ID",
            length=8,
        ),
        BadgeField(
            name="status",
            title="Status",
            label_map={
                "pending": "warning",
                "running": "info",
                "completed": "success",
                "failed": "danger",
            },
            icon=Icons.RESTORE,
        ),
        DateTimeField(
            name="created_at",
            title="Created",
            show_relative=True,
            ordering="created_at",
        ),
    ],

    # Fieldsets
    fieldsets=[
        FieldsetConfig(
            title="Restore Information",
            fields=["id", "backup", "target_database_alias"],
        ),
        FieldsetConfig(
            title="Status",
            fields=["status", "error_message", "started_at", "completed_at", "duration_seconds"],
        ),
        FieldsetConfig(
            title="Metadata",
            fields=["created_by", "created_at"],
            collapsed=True,
        ),
    ],

    # Readonly fields
    readonly_fields=[
        "id",
        "backup",
        "target_database_alias",
        "status",
        "error_message",
        "started_at",
        "completed_at",
        "duration_seconds",
        "created_at",
        "created_by",
    ],

    # Select related for optimization
    select_related=["backup"],
)


@admin.register(RestoreRecord)
class RestoreRecordAdmin(PydanticAdmin):
    """Admin interface for restore records."""

    config = restore_record_config

    def has_add_permission(self, request):
        """Disable manual creation - restores are created via backup restore."""
        return False
