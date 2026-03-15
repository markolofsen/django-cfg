"""
Management command to reset OTP throttle/rate-limit state for one or all emails.

Usage:
    uv run python manage.py otp_reset_throttle --email user@example.com
    uv run python manage.py otp_reset_throttle --all
"""

from django.core.cache import cache
from django.core.management.base import BaseCommand

from django_cfg.apps.system.accounts.services.brute_force_service import (
    _PREFIX_COOLDOWN,
    _PREFIX_DAILY,
    _PREFIX_HOURLY,
    _PREFIX_VERIFY_FAIL,
    _PREFIX_VERIFY_LOCKOUT,
    _hash_identifier,
)

_ALL_PREFIXES = [
    _PREFIX_COOLDOWN,
    _PREFIX_HOURLY,
    _PREFIX_DAILY,
    _PREFIX_VERIFY_FAIL,
    _PREFIX_VERIFY_LOCKOUT,
]


class Command(BaseCommand):
    help = "Reset OTP throttle / rate-limit cache for a specific email or all emails"

    def add_arguments(self, parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--email", type=str, help="Email address to reset")
        group.add_argument("--all", action="store_true", help="Reset ALL otp:* cache keys (dev only)")

    def handle(self, *args, **options):
        if options["all"]:
            self._reset_all()
        else:
            self._reset_email(options["email"])

    def _reset_email(self, email: str):
        email_hash = _hash_identifier(email)
        deleted = []
        for prefix in _ALL_PREFIXES:
            key = f"{prefix}:{email_hash}"
            if cache.delete(key):
                deleted.append(prefix.split(":")[-1])

        if deleted:
            self.stdout.write(self.style.SUCCESS(
                f"✅ Cleared throttle for {email}: {', '.join(deleted)}"
            ))
        else:
            self.stdout.write(self.style.WARNING(
                f"⚠️  No active throttle keys found for {email} (already clear)"
            ))

    def _reset_all(self):
        try:
            # django-redis exposes keys(); locmem doesn't
            keys_fn = getattr(cache, "keys", None)
            if callable(keys_fn):
                all_keys = list(keys_fn("otp:*"))  # type: ignore[arg-type]
                count = len(all_keys)
                for key in all_keys:
                    cache.delete(key)
                self.stdout.write(self.style.SUCCESS(
                    f"✅ Deleted {count} otp:* cache keys"
                ))
            else:
                # Fallback: clear the whole cache (locmem / file)
                cache.clear()
                self.stdout.write(self.style.WARNING(
                    "⚠️  Backend doesn't support key scan — cleared entire cache"
                ))
        except Exception as exc:
            self.stdout.write(self.style.ERROR(f"❌ Error: {exc}"))
