"""
Database Backup API Views.
"""

from django.conf import settings
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from ..models import BackupRecord, RestoreRecord
from ..services import BackupService
from .serializers import (
    BackupRecordListSerializer,
    BackupRecordSerializer,
    CreateBackupSerializer,
    CreateRestoreSerializer,
    DatabaseInfoSerializer,
    RestoreRecordSerializer,
)


class BackupViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API ViewSet for database backups.

    Provides endpoints for:
    - List backups (GET /api/db/backups/)
    - Get backup details (GET /api/db/backups/{id}/)
    - Create backup (POST /api/db/backups/create/)
    - List databases (GET /api/db/backups/databases/)
    - Cleanup old backups (POST /api/db/backups/cleanup/)
    """

    queryset = BackupRecord.objects.all()
    serializer_class = BackupRecordSerializer
    permission_classes = [IsAdminUser]
    filterset_fields = ["status", "database_alias", "database_engine", "is_scheduled"]
    search_fields = ["filename", "database_alias", "database_name"]
    ordering_fields = ["created_at", "file_size", "duration_seconds"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return BackupRecordListSerializer
        return BackupRecordSerializer

    @action(detail=False, methods=["post"])
    def create_backup(self, request):
        """
        Create a new database backup.

        Request body:
            database_alias: Database alias to backup (default: "default")

        Returns:
            BackupRecord details
        """
        serializer = CreateBackupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        database_alias = serializer.validated_data.get("database_alias", "default")

        if database_alias not in settings.DATABASES:
            return Response(
                {"error": f"Database '{database_alias}' not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        service = BackupService()

        try:
            record = service.create_backup(
                database_alias=database_alias,
                is_scheduled=False,
                is_manual=True,
            )

            return Response(
                BackupRecordSerializer(record).data,
                status=status.HTTP_201_CREATED if record.status == "completed" else status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"])
    def databases(self, request):
        """
        List configured databases with backup info.

        Returns:
            List of databases with last backup info
        """
        service = BackupService()
        databases = []

        for alias, config in settings.DATABASES.items():
            engine_type = service.detect_database_engine(alias)

            # Get last backup
            last_backup = BackupRecord.objects.filter(
                database_alias=alias,
                status="completed",
            ).first()

            # Check if backup is enabled
            backup_enabled = True
            if service.config:
                backup_enabled = service.config.should_backup_database(alias)

            databases.append({
                "alias": alias,
                "engine": engine_type,
                "name": config.get("NAME", ""),
                "host": config.get("HOST", "localhost"),
                "port": str(config.get("PORT", "")),
                "backup_enabled": backup_enabled,
                "last_backup": last_backup,
            })

        serializer = DatabaseInfoSerializer(databases, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def cleanup(self, request):
        """
        Clean up old backups according to retention policy.

        Returns:
            Success message
        """
        service = BackupService()

        try:
            service.cleanup_old_backups()
            return Response({"status": "Cleanup completed"})
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"])
    def restore(self, request, pk=None):
        """
        Restore database from this backup.

        Request body:
            target_database_alias: Target database (optional, defaults to original)

        Returns:
            RestoreRecord details
        """
        backup = self.get_object()

        if backup.status != "completed":
            return Response(
                {"error": f"Cannot restore from backup with status: {backup.status}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        target = request.data.get("target_database_alias", backup.database_alias)

        if target not in settings.DATABASES:
            return Response(
                {"error": f"Target database '{target}' not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        service = BackupService()

        try:
            record = service.restore_backup(
                backup_id=str(backup.id),
                target_database_alias=target,
                created_by=request.user.username if request.user else "api",
            )

            return Response(
                RestoreRecordSerializer(record).data,
                status=status.HTTP_201_CREATED if record.status == "completed" else status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class RestoreViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API ViewSet for database restores.

    Provides endpoints for:
    - List restores (GET /api/db/restores/)
    - Get restore details (GET /api/db/restores/{id}/)
    """

    queryset = RestoreRecord.objects.all()
    serializer_class = RestoreRecordSerializer
    permission_classes = [IsAdminUser]
    filterset_fields = ["status", "target_database_alias"]
    ordering = ["-created_at"]
