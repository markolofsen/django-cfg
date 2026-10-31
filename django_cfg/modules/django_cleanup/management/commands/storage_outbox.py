"""
Storage outbox status and manual drain.

Examples:
    manage.py storage_outbox                 # counts and the age of the oldest pending row
    manage.py storage_outbox --json
    manage.py storage_outbox --drain --dry-run   # list what would be deleted, change nothing
    manage.py storage_outbox --drain --limit 50
    manage.py storage_outbox --retry-failed      # give failed rows a fresh set of attempts

`--drain` runs the same code as the scheduled task; it is not a second scheduler.
"""

import json

from django.core.management.base import BaseCommand
from django.utils import timezone

from django_cfg.modules.django_cleanup.sync import metrics, worker


class Command(BaseCommand):
    help = "Show the storage deletion outbox, or drain it by hand."

    def add_arguments(self, parser):
        parser.add_argument("--drain", action="store_true", help="Process due rows now")
        parser.add_argument("--dry-run", action="store_true", help="With --drain: log what would be deleted, change nothing")
        parser.add_argument("--limit", type=int, default=None, help="With --drain: rows to take")
        parser.add_argument("--retry-failed", action="store_true", help="Reset failed rows to pending")
        parser.add_argument("--json", action="store_true", dest="as_json", help="Machine-readable output")

    def handle(self, *args, **options):
        from django_cfg.modules.django_cleanup.models import StorageDeletion

        result = {}
        if options["retry_failed"]:
            result["retried_failed"] = StorageDeletion.objects.filter(status=StorageDeletion.Status.FAILED).update(
                status=StorageDeletion.Status.PENDING, attempts=0, next_attempt_at=timezone.now()
            )
        if options["drain"]:
            result["drain"] = worker.drain(limit=options["limit"], dry_run=options["dry_run"] or None).as_dict()
        result["outbox"] = metrics.collect().as_dict()

        if options["as_json"]:
            self.stdout.write(json.dumps(result, indent=2))
            return
        for name, value in result.items():
            self.stdout.write(f"{name}: {value}")
