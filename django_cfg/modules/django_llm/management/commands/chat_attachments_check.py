"""
Compare the attachment table with the storage: rows whose file is gone, files no row points at.

Usage:
    python manage.py chat_attachments_check                     # counts only
    python manage.py chat_attachments_check --fix                # also delete orphan files older than --grace-hours
    python manage.py chat_attachments_check --model assistant.Thread

Only counts are printed: file names are the users' labels and never reach a log. A row without its file is reported, never deleted.
"""

from django.core.management.base import BaseCommand, CommandError

from django_cfg.modules.django_llm.agent.chat import ops


class Command(BaseCommand):
    help = "Report attachment rows without files and files without rows (counts only); --fix removes old orphan files"

    def add_arguments(self, parser):
        parser.add_argument("--model", help="app_label.ThreadModel (needed when more than one chat is installed)")
        parser.add_argument("--fix", action="store_true", help="delete orphan files older than --grace-hours")
        parser.add_argument("--grace-hours", type=float, default=24.0, help="a younger orphan may be an upload in flight (default 24)")

    def handle(self, *args, **options):
        try:
            model = ops.thread_model(options["model"])
        except ops.ThreadModelError as err:
            raise CommandError(str(err)) from err
        drift = ops.check_attachments(model, fix=options["fix"], grace_hours=options["grace_hours"])
        self.stdout.write(f"{model._meta.label}: {drift.rows} row(s), {drift.missing} without a file, {drift.orphans} orphan file(s), {drift.removed} removed")
