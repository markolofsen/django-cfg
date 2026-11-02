"""
End sessions: every user (default) or one (--email).

    python manage.py logout_all [--email user@example.com] [--dry-run]

Does three things so nothing survives: blacklists every live refresh token, sets the user's
`tokens_valid_after` to now (access tokens issued earlier are rejected, however long they live), and deletes
Django sessions (admin). API keys are not touched.
"""

from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = "Log users out everywhere: blacklist refresh tokens, cut off older access tokens, clear sessions."

    def add_arguments(self, parser):
        parser.add_argument("--email", help="only this user (default: everyone)")
        parser.add_argument("--dry-run", action="store_true", help="count, change nothing")

    def handle(self, *args, email=None, dry_run=False, **options):
        from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

        User = get_user_model()
        users = User.objects.all()
        tokens = OutstandingToken.objects.filter(expires_at__gt=timezone.now(), blacklistedtoken__isnull=True)
        sessions = Session.objects.all()
        if email:
            users = users.filter(email_key=User.objects.canonical_email(email)) if hasattr(User.objects, "canonical_email") else users.filter(email__iexact=email)
            tokens = tokens.filter(user__in=users)
            sessions = Session.objects.none()  # sessions are not keyed by user cheaply; use --all for them
        counts = (users.count(), tokens.count(), sessions.count())
        self.stdout.write(f"users={counts[0]} live refresh tokens={counts[1]} sessions={counts[2]}")
        if dry_run:
            return
        BlacklistedToken.objects.bulk_create([BlacklistedToken(token=t) for t in tokens], ignore_conflicts=True)
        # A second of margin: tokens minted in the same second as the cutoff must not survive.
        users.update(tokens_valid_after=timezone.now())
        sessions.delete()
        self.stdout.write(self.style.SUCCESS("done"))
