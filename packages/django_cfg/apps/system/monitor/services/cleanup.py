"""
Cleanup service for monitor app retention policies.

Centralises all deletion logic so it can be called from:
- management command (monitor_cleanup)
- RQ scheduled task
- tests (dry_run=True)
"""

from dataclasses import dataclass
from datetime import timedelta

from django.utils import timezone


@dataclass
class CleanupResult:
    frontend_events: int = 0
    orphan_sessions: int = 0
    server_events: int = 0

    @property
    def total(self) -> int:
        return self.frontend_events + self.orphan_sessions + self.server_events


class CleanupService:
    """
    Applies retention policies to monitor models.

    Usage:
        result = CleanupService().run(retention_days=90, dry_run=False)
        print(result.frontend_events, result.server_events)
    """

    def run(
        self,
        *,
        retention_days: int,
        server_events_retention_days: int | None = None,
        dry_run: bool = False,
    ) -> CleanupResult:
        """
        Delete stale monitor records.

        Args:
            retention_days: Delete FrontendEvent + orphan sessions older than N days.
                            0 = keep forever (skip).
            server_events_retention_days: Delete resolved ServerEvents older than N days.
                                          None = use retention_days value.
                                          0 = keep forever (skip).
            dry_run: Count only, do not delete.

        Returns:
            CleanupResult with counts of deleted (or would-be deleted) records.
        """
        result = CleanupResult()

        if server_events_retention_days is None:
            server_events_retention_days = retention_days

        if retention_days > 0:
            cutoff = timezone.now() - timedelta(days=retention_days)
            result.frontend_events = self._clean_frontend_events(cutoff, dry_run)
            result.orphan_sessions = self._clean_orphan_sessions(cutoff, dry_run)

        if server_events_retention_days > 0:
            server_cutoff = timezone.now() - timedelta(days=server_events_retention_days)
            result.server_events = self._clean_server_events(server_cutoff, dry_run)

        return result

    # ── Private helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _clean_frontend_events(cutoff, dry_run: bool) -> int:
        from django_cfg.apps.system.monitor.models import FrontendEvent

        qs = FrontendEvent.objects.filter(created_at__lt=cutoff)
        if dry_run:
            return qs.count()
        deleted, _ = qs.delete()
        return deleted

    @staticmethod
    def _clean_orphan_sessions(cutoff, dry_run: bool) -> int:
        from django_cfg.apps.system.monitor.models import AnonymousSession

        qs = AnonymousSession.objects.filter(
            user__isnull=True,
            last_seen__lt=cutoff,
            events__isnull=True,
        ).distinct()
        if dry_run:
            return qs.count()
        deleted, _ = qs.delete()
        return deleted

    @staticmethod
    def _clean_server_events(cutoff, dry_run: bool) -> int:
        from django_cfg.apps.system.monitor.models import ServerEvent

        # Only delete RESOLVED events — open bugs are never auto-purged
        qs = ServerEvent.objects.filter(
            is_resolved=True,
            last_seen__lt=cutoff,
        )
        if dry_run:
            return qs.count()
        deleted, _ = qs.delete()
        return deleted
