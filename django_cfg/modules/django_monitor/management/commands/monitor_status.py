"""
monitor_status — show D1 monitor event statistics.

Usage:
    python manage.py monitor_status
"""

from django_cfg.management.utils import SafeCommand


class Command(SafeCommand):
    command_name = "monitor_status"
    help = "Show Cloudflare D1 monitor event statistics"

    def handle(self, *args, **options):
        from django_cfg.modules.django_monitor import is_enabled

        if not is_enabled():
            self.stdout.write(self.style.ERROR("django_monitor: django_cf is not ready — check CloudflareConfig"))
            return

        try:
            from django_cfg.modules.django_monitor import get_service
            service = get_service()
            service._ensure_schema()  # create tables if not exist
            client = service._get_client()

            r_srv = client.execute("SELECT COUNT(*) as cnt FROM server_events")
            r_unresolved = client.execute("SELECT COUNT(*) as cnt FROM server_events WHERE is_resolved = '0'")
            r_fe = client.execute("SELECT COUNT(*) as cnt FROM frontend_events")

            srv_total = r_srv.results[0].get("cnt", 0) if r_srv.results else 0
            srv_open = r_unresolved.results[0].get("cnt", 0) if r_unresolved.results else 0
            fe_total = r_fe.results[0].get("cnt", 0) if r_fe.results else 0

            self.stdout.write(self.style.SUCCESS("Status: CONNECTED"))
            self.stdout.write(f"  Server events  : {srv_total} total, {srv_open} open")
            self.stdout.write(f"  Frontend events: {fe_total} total")
        except Exception as exc:
            self.stdout.write(self.style.ERROR(f"Status: ERROR — {exc}"))
