"""`python manage.py indexnow_submit` — send changed URLs to IndexNow now.

    indexnow_submit                 # the scheduled job, run by hand
    indexnow_submit --hours 72      # a wider window
    indexnow_submit --dry-run       # count and sample, send nothing
    indexnow_submit --url https://example.com/a/ --url https://example.com/b/
"""
from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError

from django_cfg.modules.django_sitemap import indexnow


class Command(BaseCommand):
    help = "Submit URLs changed in the window (or the given --url) to IndexNow."

    def add_arguments(self, parser) -> None:
        parser.add_argument("--hours", type=int, default=None, help="Window; default IndexNowConfig.window_hours.")
        parser.add_argument("--dry-run", action="store_true", help="Count and sample; send nothing.")
        parser.add_argument("--url", action="append", default=[], help="Submit these URLs instead (repeatable).")

    def handle(self, *args, hours=None, dry_run=False, url=(), **options) -> None:
        config = indexnow.get_config()
        if config is None:
            raise CommandError("IndexNow is not configured: set `indexnow = IndexNowConfig(...)` on your DjangoConfig.")

        if url:
            if dry_run:
                self.stdout.write(f"would send {len(url)} URL(s)")
                return
            result = indexnow.submit(url, config=config)
            if not result.ok:
                raise CommandError("; ".join(result.errors))
            self.stdout.write(self.style.SUCCESS(f"accepted {result.accepted} of {result.sent}"))
            return

        try:
            summary = indexnow.submit_changed(hours, dry_run=dry_run)
        except indexnow.IndexNowError as exc:
            raise CommandError(str(exc)) from exc
        self.stdout.write(self.style.SUCCESS(str(summary)))
