"""Send the welcome letter to any address, without deleting a user first.

    python manage.py send_welcome_email you@example.com
    python manage.py send_welcome_email you@example.com --locale ru
    python manage.py send_welcome_email you@example.com --all-locales
    python manage.py send_welcome_email you@example.com --as-user someone@example.com

All the logic is in ``services.welcome_preview``; this only parses arguments and
prints. It routes through the same notification path a real signup uses, so what
lands in the inbox is what a new user gets — sender name, Reply-To and
per-locale template included.

It never writes ``welcome_email_sent_at``, so the same address can be reviewed
as many times as needed.
"""

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Send the welcome letter to an address for review (does not mark it sent)"

    def add_arguments(self, parser):
        parser.add_argument("email", help="Recipient address")
        parser.add_argument(
            "--locale",
            help="Locale to render (default: the project default, or --as-user's language)",
        )
        parser.add_argument(
            "--all-locales",
            action="store_true",
            help="Send one copy per supported locale — for reviewing translations",
        )
        parser.add_argument(
            "--as-user",
            metavar="EMAIL",
            help="Render with this existing user's context and stored language",
        )

    def handle(self, *args, **options):
        from django_cfg.apps.system.accounts.services.welcome import SUPPORTED_LOCALES
        from django_cfg.apps.system.accounts.services.welcome_preview import (
            UnsupportedLocale,
            send_welcome_preview,
        )

        email = options["email"]
        locale = options.get("locale")
        as_user = options.get("as_user")

        if locale and options["all_locales"]:
            raise CommandError("--locale and --all-locales are mutually exclusive")

        user = None
        if as_user:
            from django.contrib.auth import get_user_model

            user = get_user_model().objects.filter(email__iexact=as_user).first()
            if user is None:
                raise CommandError(f"No user with email {as_user!r}")

        locales = SUPPORTED_LOCALES if options["all_locales"] else [locale]

        for tag in locales:
            try:
                used = send_welcome_preview(email, locale=tag, user=user)
            except UnsupportedLocale as exc:
                raise CommandError(str(exc)) from exc
            self.stdout.write(self.style.SUCCESS(f"  queued {used} -> {email}"))

        # The transport sends on a *daemon* thread, and a management command's
        # process exits the moment handle() returns — which kills that thread
        # mid-flight. Without this wait the command prints "queued" for a letter
        # that never left, and writes no log row either.
        self._await_sending_threads()

        count = len(locales)
        self.stdout.write(f"{count} letter{'s' if count != 1 else ''} sent.")

    @staticmethod
    def _await_sending_threads(timeout: float = 30.0) -> None:
        """Block until the email service's background threads finish."""
        import threading
        import time

        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            alive = [
                t
                for t in threading.enumerate()
                if t is not threading.current_thread() and t.daemon and t.is_alive()
            ]
            if not alive:
                return
            time.sleep(0.1)
