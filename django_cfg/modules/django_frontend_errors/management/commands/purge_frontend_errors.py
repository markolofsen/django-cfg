"""Delete stored browser errors not seen for ``--days`` days (default: the configured retention)."""

from django.core.management.base import BaseCommand, CommandError

from django_cfg.modules.django_frontend_errors.store import purge


class Command(BaseCommand):
    help = "Delete stored browser errors past the retention window."

    def add_arguments(self, parser):
        parser.add_argument("--days", type=int, default=None)
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        days = options["days"]
        if days is None:
            from django_cfg.core.state import get_current_config

            cfg = getattr(get_current_config(), "frontend_errors", None)
            days = cfg.retention_days if cfg else 30
        if days < 0:
            raise CommandError("--days must be >= 0")
        n = purge(days, dry_run=options["dry_run"])
        verb = "Would delete" if options["dry_run"] else "Deleted"
        self.stdout.write(self.style.SUCCESS(f"{verb} {n} frontend error(s) not seen for {days} days."))
