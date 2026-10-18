"""`python manage.py indexnow_submit` — run the IndexNow diff now.

    indexnow_submit                      # the scheduled job, run by hand
    indexnow_submit --dry-run            # what would be sent, send nothing
    indexnow_submit --host example.com   # one site
    indexnow_submit --reseed             # forget the state; the next run records and sends nothing
    indexnow_submit --url https://example.com/a/ --url https://example.com/b/
"""
from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError

from django_cfg.modules.django_sitemap import indexnow


class Command(BaseCommand):
    help = "Diff the sitemap sources against what IndexNow last received, and submit the changes."

    def add_arguments(self, parser) -> None:
        parser.add_argument("--dry-run", action="store_true", help="Count and sample; send and record nothing.")
        parser.add_argument("--host", default=None, help="Only this configured site.")
        parser.add_argument("--reseed", action="store_true", help="Forget the diff state and stop.")
        parser.add_argument("--url", action="append", default=[], help="Submit these URLs instead (repeatable).")

    def handle(self, *args, dry_run=False, host=None, reseed=False, url=(), **options) -> None:
        config = indexnow.get_config()
        if config is None:
            raise CommandError("IndexNow is not configured: set `indexnow = IndexNowConfig(...)` on your DjangoConfig.")

        if reseed:
            n = indexnow.reseed(host)
            self.stdout.write(self.style.SUCCESS(f"reset {n} host(s); the next run records and sends nothing"))
            return

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
            summary = indexnow.submit_changed(dry_run=dry_run, host=host)
        except indexnow.IndexNowError as exc:
            raise CommandError(str(exc)) from exc
        for name, result in summary.get("by_host", {}).items():
            self.stdout.write(f"{name}: {result}")
        if "by_host" not in summary:
            self.stdout.write(str(summary))
