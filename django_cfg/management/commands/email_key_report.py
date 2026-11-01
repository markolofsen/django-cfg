"""List emails that map to more than one live user.

Usage:
    python manage.py email_key_report

One verified email is one user. Accounts created before ``email_key`` existed
can share a key (``a.b@gmail.com`` and ``ab@gmail.com``); sign-in by that email
then picks the oldest and never merges. This command only reports; merging is
a human decision. Exit code 1 when duplicates exist.
"""

from __future__ import annotations

from django.db.models import Count

from django_cfg.management.utils import SafeCommand


class Command(SafeCommand):
    help = "Report email keys shared by more than one live user"

    def handle(self, *args, **options):
        from django_cfg.apps.system.accounts.models import CustomUser

        live = CustomUser.objects.filter(deleted_at__isnull=True).exclude(email_key="")
        keys = (
            live.values("email_key").annotate(n=Count("pk")).filter(n__gt=1).order_by("email_key")
        )
        found = 0
        for row in keys:
            found += 1
            self.stdout.write(f"{row['email_key']}  ({row['n']} users)")
            for user in live.filter(email_key=row["email_key"]).order_by("pk"):
                flags = ("staff " if user.is_staff else "") + ("verified" if user.is_email_verified else "unverified")
                self.stdout.write(f"  #{user.pk}  {user.email}  {flags.strip()}")
        if found:
            self.stdout.write(f"{found} duplicated key(s)")
            raise SystemExit(1)
        self.stdout.write("no duplicated email keys")
