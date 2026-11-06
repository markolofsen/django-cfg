"""
Close chat answers stuck in `running` (a crash, a restart) as `error` / `failed`.

Usage:
    python manage.py chat_reap                       # the only AbstractThread subclass installed
    python manage.py chat_reap --model assistant.Thread --older-than 120

Run it every minute or two from a scheduler. `--older-than` must stay above every chat kind's `timeout_s`.
"""

from django.core.management.base import BaseCommand, CommandError

from django_cfg.modules.django_llm.agent.chat import ops


class Command(BaseCommand):
    help = "Close assistant answers left running for longer than --older-than seconds as error/failed"

    def add_arguments(self, parser):
        parser.add_argument("--model", help="app_label.ThreadModel (needed when more than one chat is installed)")
        parser.add_argument("--older-than", type=float, default=ops.REAP_AFTER_S, help="seconds a run may last before it counts as dead (default 120)")

    def handle(self, *args, **options):
        try:
            model = ops.thread_model(options["model"])
        except ops.ThreadModelError as err:
            raise CommandError(str(err)) from err
        closed = ops.reap(model, older_than_s=options["older_than"])
        self.stdout.write(f"{model._meta.label}: closed {closed} stale running answer(s)")
