from django.core.management.base import BaseCommand, CommandError

from django_cfg.modules.django_notion import doctor


class Command(BaseCommand):
    help = "Check the Notion token, access to each target database and the columns (read-only; creates and changes nothing)."

    def handle(self, *args, **options):
        findings = doctor.run()
        styles = {doctor.OK: self.style.SUCCESS, doctor.WARN: self.style.WARNING, doctor.ERROR: self.style.ERROR}
        for f in findings:
            self.stdout.write(styles[f.level](f"[{f.level.upper()}] {f.where}: {f.message}"))
        if any(f.level == doctor.ERROR for f in findings):
            raise CommandError("django_notion: problems found")
