"""
Management command: monitor_cleanup

Deletes old FrontendEvent records, orphaned AnonymousSession records,
and resolved ServerEvent records.

Usage:
    python manage.py monitor_cleanup
    python manage.py monitor_cleanup --days 30
    python manage.py monitor_cleanup --dry-run
    python manage.py monitor_cleanup --days 30 --verbose
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Delete old frontend monitoring events, orphaned sessions, and resolved server events"

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=None,
            help="Delete events older than N days (default: from FrontendMonitorConfig.retention_days)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be deleted without actually deleting",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Show detailed output",
        )

    def handle(self, *args, **options):
        from django_cfg.apps.system.monitor.__cfg__ import get_settings
        from django_cfg.apps.system.monitor.services.cleanup import CleanupService

        cfg = get_settings()
        retention_days = options["days"] if options["days"] is not None else cfg.retention_days
        server_retention_days = options["days"] if options["days"] is not None else cfg.server_events_retention_days
        dry_run = options["dry_run"]
        verbose = options["verbose"]

        if retention_days == 0 and server_retention_days == 0:
            self.stdout.write(self.style.WARNING("retention_days=0 — keeping all records forever, nothing to do."))
            return

        if verbose or dry_run:
            from django.utils import timezone
            from datetime import timedelta
            if retention_days > 0:
                cutoff = timezone.now() - timedelta(days=retention_days)
                self.stdout.write(f"Frontend cutoff: {cutoff.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            if server_retention_days > 0:
                server_cutoff = timezone.now() - timedelta(days=server_retention_days)
                self.stdout.write(f"Server events cutoff: {server_cutoff.strftime('%Y-%m-%d %H:%M:%S UTC')}")

        result = CleanupService().run(
            retention_days=retention_days,
            server_events_retention_days=server_retention_days,
            dry_run=dry_run,
        )

        prefix = "[dry-run] Would delete" if dry_run else "Deleted"
        style = self.style.WARNING if dry_run else self.style.SUCCESS

        if retention_days > 0:
            self.stdout.write(style(f"{prefix} {result.frontend_events} FrontendEvent records"))
            self.stdout.write(style(f"{prefix} {result.orphan_sessions} orphaned AnonymousSession records"))

        if server_retention_days > 0:
            self.stdout.write(style(f"{prefix} {result.server_events} resolved ServerEvent records"))

        if dry_run:
            self.stdout.write(self.style.WARNING("Dry run complete — nothing was deleted."))
