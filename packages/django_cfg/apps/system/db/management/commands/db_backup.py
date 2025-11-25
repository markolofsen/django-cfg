"""
Database Backup Management Command.

Creates database backups manually. Use this when Django-RQ is not enabled
or for ad-hoc backups.

Usage:
    # Backup default database
    python manage.py db_backup

    # Backup specific database
    python manage.py db_backup --database=vehicles

    # Backup all databases
    python manage.py db_backup --all

    # List recent backups
    python manage.py db_backup --list

    # Show backup info
    python manage.py db_backup --info <backup_id>
"""

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from django_cfg.apps.system.db.services import BackupService


class Command(BaseCommand):
    help = "Create database backups"

    def add_arguments(self, parser):
        parser.add_argument(
            "--database",
            "-d",
            type=str,
            default="default",
            help="Database alias to backup (default: default)",
        )

        parser.add_argument(
            "--all",
            "-a",
            action="store_true",
            help="Backup all databases",
        )

        parser.add_argument(
            "--list",
            "-l",
            action="store_true",
            help="List recent backups",
        )

        parser.add_argument(
            "--info",
            type=str,
            help="Show details for specific backup ID",
        )

        parser.add_argument(
            "--limit",
            type=int,
            default=10,
            help="Number of backups to list (default: 10)",
        )

        parser.add_argument(
            "--cleanup",
            action="store_true",
            help="Clean up old backups according to retention policy",
        )

    def handle(self, *args, **options):
        service = BackupService()

        if options["list"]:
            self._list_backups(options["limit"])
            return

        if options["info"]:
            self._show_backup_info(options["info"])
            return

        if options["cleanup"]:
            self._cleanup_backups(service)
            return

        if options["all"]:
            self._backup_all_databases(service)
        else:
            self._backup_database(service, options["database"])

    def _backup_database(self, service: BackupService, database_alias: str):
        """Backup a single database."""
        if database_alias not in settings.DATABASES:
            raise CommandError(f"Database '{database_alias}' not found in settings")

        self.stdout.write(f"Starting backup for database: {database_alias}")

        try:
            record = service.create_backup(
                database_alias=database_alias,
                is_scheduled=False,
                is_manual=True,
            )

            if record.status == "completed":
                self.stdout.write(
                    self.style.SUCCESS(
                        f"\nBackup completed successfully!\n"
                        f"  File: {record.filename}\n"
                        f"  Size: {record.file_size_human}\n"
                        f"  Duration: {record.duration_human}\n"
                        f"  Path: {record.file_path}\n"
                        f"  ID: {record.id}"
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f"\nBackup failed!\n"
                        f"  Error: {record.error_message}"
                    )
                )

        except Exception as e:
            raise CommandError(f"Backup failed: {e}")

    def _backup_all_databases(self, service: BackupService):
        """Backup all configured databases."""
        databases = list(settings.DATABASES.keys())
        self.stdout.write(f"Backing up {len(databases)} databases...")

        success_count = 0
        failed_count = 0

        for alias in databases:
            if service.config and not service.config.should_backup_database(alias):
                self.stdout.write(f"  Skipping {alias} (disabled in config)")
                continue

            self.stdout.write(f"  Backing up {alias}...")

            try:
                record = service.create_backup(
                    database_alias=alias,
                    is_scheduled=False,
                    is_manual=True,
                )

                if record.status == "completed":
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"    ✓ {record.filename} ({record.file_size_human})"
                        )
                    )
                    success_count += 1
                else:
                    self.stdout.write(
                        self.style.ERROR(f"    ✗ Failed: {record.error_message}")
                    )
                    failed_count += 1

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"    ✗ Error: {e}"))
                failed_count += 1

        self.stdout.write(
            f"\nCompleted: {success_count} succeeded, {failed_count} failed"
        )

    def _list_backups(self, limit: int):
        """List recent backups."""
        from django_cfg.apps.system.db.models import BackupRecord

        backups = BackupRecord.objects.all()[:limit]

        if not backups:
            self.stdout.write("No backups found")
            return

        self.stdout.write(f"\nRecent backups (showing {len(backups)}):\n")

        for backup in backups:
            status_style = {
                "completed": self.style.SUCCESS,
                "failed": self.style.ERROR,
                "running": self.style.WARNING,
                "pending": self.style.WARNING,
                "deleted": self.style.NOTICE,
            }.get(backup.status, self.style.NOTICE)

            self.stdout.write(
                f"  {backup.id}\n"
                f"    Database: {backup.database_alias} ({backup.database_engine})\n"
                f"    File: {backup.filename}\n"
                f"    Size: {backup.file_size_human}\n"
                f"    Status: {status_style(backup.status)}\n"
                f"    Created: {backup.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
            )

    def _show_backup_info(self, backup_id: str):
        """Show details for specific backup."""
        from django_cfg.apps.system.db.models import BackupRecord

        try:
            backup = BackupRecord.objects.get(id=backup_id)
        except BackupRecord.DoesNotExist:
            raise CommandError(f"Backup not found: {backup_id}")

        self.stdout.write(f"\nBackup Details: {backup.id}\n")
        self.stdout.write(f"  Database Alias: {backup.database_alias}")
        self.stdout.write(f"  Database Name: {backup.database_name}")
        self.stdout.write(f"  Database Engine: {backup.database_engine}")
        self.stdout.write(f"  Filename: {backup.filename}")
        self.stdout.write(f"  File Path: {backup.file_path}")
        self.stdout.write(f"  File Size: {backup.file_size_human}")
        self.stdout.write(f"  Compression: {backup.compression}")
        self.stdout.write(f"  Encrypted: {backup.encrypted}")
        self.stdout.write(f"  Storage Backend: {backup.storage_backend}")
        self.stdout.write(f"  Status: {backup.status}")
        self.stdout.write(f"  Duration: {backup.duration_human}")
        self.stdout.write(f"  Tables Count: {backup.tables_count or 'N/A'}")
        self.stdout.write(f"  Rows Count: {backup.rows_count or 'N/A'}")
        self.stdout.write(f"  Checksum: {backup.checksum or 'N/A'}")
        self.stdout.write(f"  Created: {backup.created_at}")
        self.stdout.write(f"  Scheduled: {backup.is_scheduled}")
        self.stdout.write(f"  Manual: {backup.is_manual}")

        if backup.error_message:
            self.stdout.write(self.style.ERROR(f"  Error: {backup.error_message}"))

    def _cleanup_backups(self, service: BackupService):
        """Clean up old backups."""
        self.stdout.write("Cleaning up old backups...")

        try:
            service.cleanup_old_backups()
            self.stdout.write(self.style.SUCCESS("Cleanup completed"))
        except Exception as e:
            raise CommandError(f"Cleanup failed: {e}")
