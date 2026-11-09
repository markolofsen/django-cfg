"""
Delete idle chat sessions (and their messages) older than N days.

Usage:
    python manage.py chat_prune --dry-run            # count only
    python manage.py chat_prune --days 180 --model assistant.Thread [--kind support]

Last activity is the newest message (the thread's creation when it has none). Only counts are printed: titles and
messages are the users' text and never reach a log.
"""

from django.core.management.base import BaseCommand, CommandError

from django_cfg.modules.django_llm.agent.chat import ops


class Command(BaseCommand):
    help = "Delete chat threads idle for more than --days days (messages go with them)"

    def add_arguments(self, parser):
        parser.add_argument("--model", help="app_label.ThreadModel (needed when more than one chat is installed)")
        parser.add_argument("--days", type=int, default=ops.PRUNE_AFTER_DAYS, help="idle days before a thread is dropped (default 180)")
        parser.add_argument("--kind", help="only threads of this chat kind")
        parser.add_argument("--batch", type=int, default=500, help="threads deleted per transaction")
        parser.add_argument("--dry-run", action="store_true", help="count what would go; delete nothing")

    def handle(self, *args, **options):
        try:
            model = ops.thread_model(options["model"])
            result = ops.prune(model, days=options["days"], kind=options["kind"], dry_run=options["dry_run"], batch=options["batch"])
        except (ops.ThreadModelError, ValueError) as err:
            raise CommandError(str(err)) from err
        verb = "would delete" if options["dry_run"] else "deleted"
        self.stdout.write(f"{model._meta.label}: {verb} {result.threads} thread(s), {result.messages} message(s), {result.files} file(s) idle for over {options['days']} days")
