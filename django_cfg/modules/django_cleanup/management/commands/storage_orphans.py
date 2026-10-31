"""
Find files in storage that no registered owner claims. Report only.

Examples:
    manage.py storage_orphans                  # scan allowed_prefixes, print a sample
    manage.py storage_orphans --json --limit 5000
    manage.py storage_orphans --enqueue        # write the orphans to the outbox (the worker still applies the guard)

Needs `allowed_prefixes` (the roots to scan) and, for every registration on a
storage, an `all_keys` callable; without it an orphan cannot be told from a
live file, so that storage is skipped. Rows removed with a raw delete or a
database cascade never fire a signal; this scan is how they are found.
"""

import json

from django.core.files.storage import storages
from django.core.management.base import BaseCommand
from django.utils import timezone

from django_cfg.modules.django_cleanup.config import get_config
from django_cfg.modules.django_cleanup.sync.guard import normalize_prefixes
from django_cfg.modules.django_cleanup.sync.owned import all_registrations
from django_cfg.modules.django_cleanup.sync.storage_walk import walk


def _is_live(key: str, exact: set, prefixes: set) -> bool:
    if key in exact:
        return True
    cut = key.find("/")
    while cut != -1:
        if key[: cut + 1] in prefixes:
            return True
        cut = key.find("/", cut + 1)
    return False


class Command(BaseCommand):
    help = "Report storage files no registered owner claims (never deletes)."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=1000, help="Orphans to list")
        parser.add_argument("--enqueue", action="store_true", help="Queue the listed orphans in the outbox")
        parser.add_argument("--json", action="store_true", dest="as_json")

    def handle(self, *args, **options):
        config = get_config()
        roots = normalize_prefixes(config.allowed_prefixes)
        registrations = all_registrations()
        report = {"scanned": 0, "orphans": [], "skipped_storages": {}, "truncated": False}

        if not roots or not registrations:
            report["error"] = "needs allowed_prefixes and at least one register_owned_files()"
        else:
            for alias in sorted({r.storage for r in registrations}):
                entries = [r for r in registrations if r.storage == alias]
                if any(r.all_keys is None for r in entries):
                    report["skipped_storages"][alias] = "a registration has no all_keys"
                    continue
                exact, prefixes = set(), set()
                for entry in entries:
                    for key in entry.all_keys():
                        (prefixes if key.endswith("/") else exact).add(key)
                storage = storages[alias]
                for root in roots:
                    for key in walk(storage, root):
                        report["scanned"] += 1
                        if _is_live(key, exact, prefixes):
                            continue
                        if len(report["orphans"]) >= options["limit"]:
                            report["truncated"] = True
                            break
                        report["orphans"].append({"storage": alias, "key": key})

        if options["enqueue"] and report["orphans"]:
            from django_cfg.modules.django_cleanup.models import StorageDeletion

            now = timezone.now()
            StorageDeletion.objects.bulk_create(
                [
                    StorageDeletion(storage_alias=o["storage"], key=o["key"], model_label="orphan-scan", next_attempt_at=now)
                    for o in report["orphans"]
                ]
            )
            report["enqueued"] = len(report["orphans"])

        if options["as_json"]:
            self.stdout.write(json.dumps(report, indent=2))
            return
        self.stdout.write(f"scanned {report['scanned']} files, {len(report['orphans'])} orphans" + (" (truncated)" if report["truncated"] else ""))
        for alias, why in report["skipped_storages"].items():
            self.stdout.write(f"skipped storage {alias}: {why}")
        if "error" in report:
            self.stdout.write(report["error"])
        for orphan in report["orphans"]:
            self.stdout.write(f"  {orphan['storage']}:{orphan['key']}")
