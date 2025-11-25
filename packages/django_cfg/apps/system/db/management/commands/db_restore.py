"""
Database Restore Management Command.

Restores database from backup.

Usage:
    # Restore to original database
    python manage.py db_restore <backup_id>

    # Restore to different database
    python manage.py db_restore <backup_id> --target=test_db

    # Force restore without confirmation
    python manage.py db_restore <backup_id> --force
"""

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from django_cfg.apps.system.db.services import BackupService


class Command(BaseCommand):
    help = "Restore database from backup"

    def add_arguments(self, parser):
        parser.add_argument(
            "backup_id",
            type=str,
            help="Backup ID (UUID) to restore",
        )

        parser.add_argument(
            "--target",
            "-t",
            type=str,
            help="Target database alias (defaults to original database)",
        )

        parser.add_argument(
            "--force",
            "-f",
            action="store_true",
            help="Skip confirmation prompt",
        )

    def handle(self, *args, **options):
        from django_cfg.apps.system.db.models import BackupRecord

        backup_id = options["backup_id"]
        target_database = options["target"]
        force = options["force"]

        # Get backup record
        try:
            backup = BackupRecord.objects.get(id=backup_id)
        except BackupRecord.DoesNotExist:
            raise CommandError(f"Backup not found: {backup_id}")

        if backup.status == "deleted":
            raise CommandError("Cannot restore from deleted backup (file removed)")

        if backup.status != "completed":
            raise CommandError(f"Cannot restore from backup with status: {backup.status}")

        # Determine target database
        target = target_database or backup.database_alias

        if target not in settings.DATABASES:
            raise CommandError(f"Target database '{target}' not found in settings")

        # Confirmation
        if not force:
            self.stdout.write(
                self.style.WARNING(
                    f"\nWARNING: This will restore database '{target}' from backup!\n"
                    f"  Backup: {backup.filename}\n"
                    f"  Created: {backup.created_at}\n"
                    f"  Size: {backup.file_size_human}\n"
                    f"\n  ALL EXISTING DATA IN '{target}' WILL BE OVERWRITTEN!\n"
                )
            )

            confirm = input("Type 'yes' to confirm: ")
            if confirm.lower() != "yes":
                self.stdout.write("Restore cancelled")
                return

        # Perform restore
        self.stdout.write(f"\nRestoring {backup.filename} to {target}...")

        service = BackupService()

        try:
            record = service.restore_backup(
                backup_id=str(backup.id),
                target_database_alias=target,
                created_by="management_command",
            )

            if record.status == "completed":
                self.stdout.write(
                    self.style.SUCCESS(
                        f"\nRestore completed successfully!\n"
                        f"  Target: {target}\n"
                        f"  Duration: {record.duration_seconds:.1f}s"
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f"\nRestore failed!\n"
                        f"  Error: {record.error_message}"
                    )
                )

        except Exception as e:
            raise CommandError(f"Restore failed: {e}")
