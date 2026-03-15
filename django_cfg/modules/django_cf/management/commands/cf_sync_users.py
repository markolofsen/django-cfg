"""
cf_sync_users — bulk-sync all Django users to Cloudflare D1.

Usage:
    python manage.py cf_sync_users
"""

from django_cfg.management.utils import SafeCommand


class Command(SafeCommand):
    command_name = "cf_sync_users"
    help = "Bulk-upsert all Django users to Cloudflare D1"

    def handle(self, *args, **options):
        from django_cfg.modules.django_cf import is_ready
        if not is_ready():
            self.stdout.write(self.style.ERROR("CloudflareConfig is not ready — check credentials"))
            return

        self.stdout.write("Syncing all users to Cloudflare D1...")
        from django_cfg.modules.django_cf.users.service import UserSyncService
        stats = UserSyncService().full_sync_users()
        self.stdout.write(self.style.SUCCESS(
            f"Done — synced: {stats['synced']}, failed: {stats['failed']}"
        ))
