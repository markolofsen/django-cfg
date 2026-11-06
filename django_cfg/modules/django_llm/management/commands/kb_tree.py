"""
Print the knowledge tree exactly as the model sees it.

Usage:
    python manage.py kb_tree
    python manage.py kb_tree --path guides --depth 3 --max-chars 8000
"""

from django.core.management.base import BaseCommand, CommandError

from django_cfg.modules.django_llm.agent.chat.knowledge.tree import render_tree
from django_cfg.modules.django_llm.management.commands._kb import add_dir_argument, open_base


class Command(BaseCommand):
    help = "Print the chat knowledge-base tree"

    def add_arguments(self, parser):
        add_dir_argument(parser)
        parser.add_argument("--path", default="", help="a directory of the tree")
        parser.add_argument("--depth", type=int, default=2)
        parser.add_argument("--max-chars", type=int, default=6000, help="6000 is the prompt prefix cap, 8000 the kb_tree tool cap")

    def handle(self, *args, **options):
        base = open_base(options)
        try:
            self.stdout.write(render_tree(base.entries(), options["path"], options["depth"], options["max_chars"]))
        except KeyError as exc:
            raise CommandError(f"{exc.args[0]!r} is not a directory of the knowledge base") from None
