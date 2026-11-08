"""
log_prune - delete old or surplus django-cfg log files.

Dry run by default: it lists what it would delete, with sizes. ``--apply`` deletes.
Only files django-cfg writes are touched (``django.log*``, ``djangocfg/*`` and the
names older versions created). A live file is never deleted.

    python manage.py log_prune                    # dry run on the resolved log dir
    python manage.py log_prune --dir ./logs --apply
    python manage.py log_prune --days 7 --keep 3 --max-mb 200 --apply

django-cfg also runs this at boot, at most once a day, in a background thread.
"""
from __future__ import annotations

from pathlib import Path

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Delete old or surplus django-cfg log files (dry run unless --apply)"

    def add_arguments(self, parser):
        parser.add_argument("--dir", help="Directory to prune (default: the configured log dir and the monitor-event dir)")
        parser.add_argument("--days", type=int, help="Delete rotated files older than this (default 14, logging.retain_days / DJANGO_CFG_LOG_RETAIN_DAYS)")
        parser.add_argument("--keep", type=int, help="Rotated files kept per log (default 5, logging.backups / DJANGO_CFG_LOG_BACKUPS)")
        parser.add_argument("--max-mb", type=int, help="Directory cap in MB (default 500, DJANGO_CFG_LOG_DIR_MAX_BYTES)")
        parser.add_argument("--apply", action="store_true", help="Actually delete (default is a dry run)")

    def handle(self, *args, **options):
        from django_cfg.modules.django_logging import maintenance

        if options["dir"]:
            dirs = [Path(options["dir"])]
        else:
            dirs = maintenance.target_dirs()
        if not dirs:
            self.stdout.write("No writable log directory: logs go to stdout. Nothing to prune.")
            return
        cap = options["max_mb"] * 1048576 if options["max_mb"] is not None else None
        for directory in dirs:
            if not directory.is_dir():
                if options["dir"]:
                    raise CommandError(f"{directory} is not a directory")
                continue  # a default location nothing has written to yet
            result = maintenance.prune_log_dir(
                directory,
                keep_days=options["days"],
                backups=options["keep"],
                cap=cap,
                dry_run=not options["apply"],
            )
            verb = "Deleted" if options["apply"] else "Would delete"
            self.stdout.write(f"{directory}: {result.total_before / 1048576:.1f} MB in django-cfg files")
            for f in result.deleted:
                self.stdout.write(f"  {verb.lower()} {f.path.relative_to(directory)}  {f.size / 1048576:.1f} MB")
            self.stdout.write(
                f"{verb} {len(result.deleted)} file(s), {result.freed / 1048576:.1f} MB; "
                f"{result.total_after / 1048576:.1f} MB left."
            )
            if not options["apply"] and result.deleted:
                self.stdout.write("Dry run. Add --apply to delete.")
            if result.over_cap:
                self.stdout.write(self.style.WARNING(
                    f"Still over the {result.cap / 1048576:.0f} MB cap: the rest is live files. "
                    "They rotate at logging.rotate_mb; lower it or logging.backups."
                ))
