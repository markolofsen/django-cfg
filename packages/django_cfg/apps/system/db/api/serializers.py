"""
Database Backup API Serializers.
"""

from rest_framework import serializers

from ..models import BackupRecord, RestoreRecord


class BackupRecordSerializer(serializers.ModelSerializer):
    """Serializer for backup records."""

    file_size_human = serializers.ReadOnlyField()
    duration_human = serializers.ReadOnlyField()

    class Meta:
        model = BackupRecord
        fields = [
            "id",
            "database_alias",
            "database_name",
            "database_engine",
            "filename",
            "file_path",
            "file_size",
            "file_size_human",
            "compression",
            "encrypted",
            "storage_backend",
            "storage_bucket",
            "status",
            "error_message",
            "started_at",
            "completed_at",
            "duration_seconds",
            "duration_human",
            "created_at",
            "is_scheduled",
            "is_manual",
            "tables_count",
            "rows_count",
            "checksum",
        ]
        read_only_fields = fields


class BackupRecordListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for backup list."""

    file_size_human = serializers.ReadOnlyField()
    duration_human = serializers.ReadOnlyField()

    class Meta:
        model = BackupRecord
        fields = [
            "id",
            "database_alias",
            "database_engine",
            "filename",
            "file_size_human",
            "status",
            "duration_human",
            "created_at",
            "is_scheduled",
        ]


class CreateBackupSerializer(serializers.Serializer):
    """Serializer for creating backup."""

    database_alias = serializers.CharField(
        default="default",
        help_text="Database alias to backup",
    )


class RestoreRecordSerializer(serializers.ModelSerializer):
    """Serializer for restore records."""

    backup_filename = serializers.CharField(
        source="backup.filename",
        read_only=True,
    )

    class Meta:
        model = RestoreRecord
        fields = [
            "id",
            "backup",
            "backup_filename",
            "target_database_alias",
            "status",
            "error_message",
            "started_at",
            "completed_at",
            "duration_seconds",
            "created_at",
            "created_by",
        ]
        read_only_fields = fields


class CreateRestoreSerializer(serializers.Serializer):
    """Serializer for creating restore."""

    backup_id = serializers.UUIDField(
        help_text="Backup ID to restore from",
    )
    target_database_alias = serializers.CharField(
        required=False,
        help_text="Target database (defaults to original)",
    )


class DatabaseInfoSerializer(serializers.Serializer):
    """Serializer for database information."""

    alias = serializers.CharField()
    engine = serializers.CharField()
    name = serializers.CharField()
    host = serializers.CharField()
    port = serializers.CharField()
    backup_enabled = serializers.BooleanField()
    last_backup = BackupRecordListSerializer(allow_null=True)
