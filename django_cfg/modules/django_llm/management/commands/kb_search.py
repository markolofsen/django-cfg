"""
Try the knowledge index from the shell.

Usage:
    python manage.py kb_search "reset password"
    python manage.py kb_search "сбросить пароль" --path guides --limit 10
"""

from django.core.management.base import BaseCommand, CommandError

from django_cfg.modules.django_llm.agent.chat.knowledge import KbError
from django_cfg.modules.django_llm.management.commands._kb import add_dir_argument, open_base


class Command(BaseCommand):
    help = "Search the chat knowledge-base index"

    def add_arguments(self, parser):
        add_dir_argument(parser)
        parser.add_argument("query")
        parser.add_argument("--path", default="", help="limit to a directory")
        parser.add_argument("--limit", type=int, default=8)

    def handle(self, *args, **options):
        base = open_base(options)
        try:
            hits = base.search(options["query"], path_prefix=options["path"], limit=options["limit"])
        except KbError as exc:
            raise CommandError(str(exc)) from None
        for h in hits:
            self.stdout.write(f"{h.path}:{h.start}-{h.end} | {h.crumb or h.title} | L{h.snippet_line}: {h.snippet}")
        if not hits:
            self.stdout.write("no matches")
