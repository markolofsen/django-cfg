"""
Management command: frontend_monitor_cleanup

Deletes old FrontendEvent records and orphaned AnonymousSession records.

Usage:
    python manage.py frontend_monitor_cleanup
    python manage.py frontend_monitor_cleanup --days 30
    python manage.py frontend_monitor_cleanup --dry-run
    python manage.py frontend_monitor_cleanup --days 30 --verbose
"""

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = "Delete old frontend monitoring events and orphaned sessions"

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
        from django_cfg.apps.system.frontend_monitor.__cfg__ import get_settings
        from django_cfg.apps.system.frontend_monitor.models import AnonymousSession, FrontendEvent

        settings = get_settings()
        retention_days = options["days"] or settings.retention_days
        dry_run = options["dry_run"]
        verbose = options["verbose"]

        if retention_days == 0:
            self.stdout.write(self.style.WARNING("retention_days=0 — keeping all events forever, nothing to do."))
            return

        cutoff = timezone.now() - timedelta(days=retention_days)

        if verbose or dry_run:
            self.stdout.write(f"Cutoff date: {cutoff.strftime('%Y-%m-%d %H:%M:%S UTC')}")

        # ── Events ────────────────────────────────────────────────────────────
        events_qs = FrontendEvent.objects.filter(created_at__lt=cutoff)
        events_count = events_qs.count()

        if dry_run:
            self.stdout.write(f"[dry-run] Would delete {events_count} FrontendEvent records")
        else:
            deleted, _ = events_qs.delete()
            self.stdout.write(
                self.style.SUCCESS(f"Deleted {deleted} FrontendEvent records older than {retention_days} days")
            )

        # ── Orphaned sessions ─────────────────────────────────────────────────
        # Sessions with no events, no linked user, and last_seen before cutoff
        orphan_qs = AnonymousSession.objects.filter(
            user__isnull=True,
            last_seen__lt=cutoff,
            events__isnull=True,
        ).distinct()
        orphan_count = orphan_qs.count()

        if dry_run:
            self.stdout.write(f"[dry-run] Would delete {orphan_count} orphaned AnonymousSession records")
        else:
            deleted_sessions, _ = orphan_qs.delete()
            self.stdout.write(
                self.style.SUCCESS(f"Deleted {deleted_sessions} orphaned AnonymousSession records")
            )

        if dry_run:
            self.stdout.write(self.style.WARNING("Dry run complete — nothing was deleted."))
