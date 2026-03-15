"""
monitor_cleanup — delete old resolved server events from D1.

Usage:
    python manage.py monitor_cleanup
    python manage.py monitor_cleanup --days 30
    python manage.py monitor_cleanup --type frontend --days 90
"""

from django_cfg.management.utils import SafeCommand


class Command(SafeCommand):
    command_name = "monitor_cleanup"
    help = "Delete old resolved events from Cloudflare D1 monitor tables"

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=90,
            help="Delete events older than N days (default: 90)",
        )
        parser.add_argument(
            "--type",
            choices=["server", "frontend", "all"],
            default="all",
            help="Which table to clean up (default: all)",
        )

    def handle(self, *args, **options):
        from django_cfg.modules.django_monitor import is_enabled

        if not is_enabled():
            self.stdout.write(self.style.ERROR("django_monitor: django_cf is not ready — check CloudflareConfig"))
            return

        days = options["days"]
        cleanup_type = options["type"]

        try:
            from django_cfg.modules.django_monitor import get_service
            service = get_service()
            client = service._get_client()

            cutoff = f"datetime('now', '-{days} days')"

            if cleanup_type in ("server", "all"):
                result = client.execute(
                    f"DELETE FROM server_events WHERE is_resolved = '1' AND last_seen < {cutoff}"
                )
                self.stdout.write(
                    self.style.SUCCESS(f"Server events deleted: {result.changes} (resolved, older than {days}d)")
                )

            if cleanup_type in ("frontend", "all"):
                result = client.execute(
                    f"DELETE FROM frontend_events WHERE created_at < {cutoff}"
                )
                self.stdout.write(
                    self.style.SUCCESS(f"Frontend events deleted: {result.changes} (older than {days}d)")
                )

        except Exception as exc:
            self.stdout.write(self.style.ERROR(f"Cleanup failed: {exc}"))
