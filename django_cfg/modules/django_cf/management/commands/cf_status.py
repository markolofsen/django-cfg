"""
cf_status — show Cloudflare D1 connection status and project/user counts.

Usage:
    python manage.py cf_status
"""

from django_cfg.management.utils import SafeCommand


class Command(SafeCommand):
    command_name = "cf_status"
    help = "Show Cloudflare D1 connection status and sync statistics"

    def handle(self, *args, **options):
        from django_cfg.modules.django_cf import _get_config, is_ready

        config = _get_config()
        if config is None:
            self.stdout.write(self.style.ERROR("CloudflareConfig: not configured"))
            return

        self.stdout.write(f"  enabled     : {config.enabled}")
        self.stdout.write(f"  account_id  : {config.account_id[:8]}..." if config.account_id else "  account_id  : (not set)")
        self.stdout.write(f"  database_id : {config.d1_database_id[:8]}..." if config.d1_database_id else "  database_id : (not set)")

        if not is_ready():
            self.stdout.write(self.style.WARNING("Status: NOT READY — credentials missing or disabled"))
            return

        try:
            from django_cfg.modules.django_cf.users.service import UserSyncService
            from django.contrib.auth import get_user_model

            User = get_user_model()
            total_users = User.objects.count()
            self.stdout.write(self.style.SUCCESS("Status: READY"))
            self.stdout.write(f"  Django users: {total_users}")

            # Quick connectivity check
            service = UserSyncService()
            client = service._get_client()
            result = client.execute("SELECT COUNT(*) as cnt FROM users")
            d1_count = result.results[0].get("cnt", "?") if result.results else "?"
            self.stdout.write(f"  D1 users    : {d1_count}")
        except Exception as exc:
            self.stdout.write(self.style.ERROR(f"Status: ERROR — {exc}"))
