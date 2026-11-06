"""
Lint the chat knowledge folder: front matter, dead links, oversize files, tree size, duplicate titles, skipped files.

Usage:
    python manage.py kb_check
    python manage.py kb_check --dir knowledge --strict      # warnings fail too (for CI)

The last line is `kb_check: OK|FAILED errors=N warnings=N files=N ...` (grep for `^kb_check:`).
Exit status 1 when there is an error (or a warning with --strict).
"""

from django.core.management.base import BaseCommand, CommandError

from django_cfg.modules.django_llm.agent.chat.knowledge.check import check_dir
from django_cfg.modules.django_llm.management.commands._kb import add_dir_argument, open_base


class Command(BaseCommand):
    help = "Lint the chat knowledge-base folder"

    def add_arguments(self, parser):
        add_dir_argument(parser)
        parser.add_argument("--strict", action="store_true", help="warnings fail the check too")

    def handle(self, *args, **options):
        base = open_base(options)
        report = check_dir(base.root, strict=options["strict"])
        for problem in report.problems:
            self.stdout.write(str(problem))
        # the summary is the last line of output, whatever the project printed while starting up: `grep '^kb_check:'`
        self.stdout.write(report.summary())
        if not report.ok():
            raise CommandError(f"kb_check: FAILED errors={report.count('error')} warnings={report.count('warning')}")
