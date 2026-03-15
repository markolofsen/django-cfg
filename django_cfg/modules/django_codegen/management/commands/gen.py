"""
Unified client generation command.

Usage:
    python manage.py gen                        # all targets, all languages
    python manage.py gen --ts                   # typescript only
    python manage.py gen --target admin         # specific target type
    python manage.py gen --ts --target admin    # combined
    python manage.py gen --groups profiles      # specific groups
    python manage.py gen --list-targets         # show configured targets
    python manage.py gen --dry-run              # preview
"""

from django.core.management.base import BaseCommand

from django_cfg.modules.django_codegen import run
from django_cfg.modules.django_codegen.config_inspector import inspect_config


class Command(BaseCommand):
    help = "Generate API clients based on generation.py config"

    def add_arguments(self, parser):
        lang_group = parser.add_argument_group("Language filters")
        lang_group.add_argument("--ts", action="store_true", help="TypeScript only")
        lang_group.add_argument("--py", action="store_true", help="Python only")
        lang_group.add_argument("--go", action="store_true", help="Go only")
        lang_group.add_argument("--swift", action="store_true", help="Swift only")

        parser.add_argument("--target", "-t", type=str, help="Target type: admin, packages, extensions, parsers, sdk, web")
        parser.add_argument("--groups", nargs="+", help="Specific groups only")
        parser.add_argument("--dry-run", action="store_true", help="Preview without changes")
        parser.add_argument("--list-targets", action="store_true", help="List all configured targets")

    def handle(self, *args, **options):
        try:
            from generation import config
        except ImportError:
            self.stderr.write(self.style.ERROR(
                "No generation.py found in project root.\n"
                "Create generation.py with your Config definition."
            ))
            return

        if options.get("list_targets"):
            self._print_summary(config)
            return

        lang_flags = {"ts": "typescript", "py": "python", "go": "go", "swift": "swift"}
        only_platforms = [lang for flag, lang in lang_flags.items() if options.get(flag)] or None

        result = run(
            config,
            only_platforms=only_platforms,
            only_target=options.get("target"),
            only_groups=options.get("groups"),
            dry_run=options.get("dry_run", False),
            verbose=options.get("verbose", False),
        )

        for error in result.stats.errors:
            self.stderr.write(self.style.ERROR(error))

    def _print_summary(self, config) -> None:
        """Print config summary using ConfigSummary."""
        summary = inspect_config(config)
        w = self.stdout.write

        if summary.openapi:
            w("\nOpenAPI targets:")
            by_lang: dict = {}
            for t in summary.openapi:
                by_lang.setdefault(t.lang, []).append(t)
            for lang, targets in by_lang.items():
                w(f"\n  {lang}:")
                for t in targets:
                    w(f"    [{t.type}] {t.path}")
                    w(f"         groups: {', '.join(t.groups)}")
                    if t.post_build:
                        w(f"         post_build: {t.post_build}")

        if summary.extensions:
            ext = summary.extensions
            if ext.targets:
                w(f"\n  extensions (auto-discovered from {ext.source_path}):")
                for t in ext.targets:
                    w(f"    [{t.groups[0]}] {t.path}")
                    if t.post_build:
                        w(f"         post_build: {t.post_build}")
            else:
                w(f"\n  extensions (none found in {ext.source_path})")

        if summary.centrifugo:
            w("\n\nCentrifugo:")
            for t in summary.centrifugo:
                w(f"\n  {t.lang}:")
                w(f"    [{t.type}] {t.path}")
                w(f"         groups: {', '.join(t.groups)}")

        if summary.sdk:
            w("\n\nSDK Packages:")
            for pkg in summary.sdk:
                w(f"\n  {pkg.name}:")
                w(f"    platform: {pkg.platform}")
                w(f"    target: {pkg.target}")
                w(f"    groups: {', '.join(pkg.groups)}")

        if summary.orm:
            w("\n\nORM (FastAPI/SQLModel):")
            for t in summary.orm:
                w(f"\n  [{t.generator}] {t.output}")
                w(f"         apps: {', '.join(t.apps) if t.apps else '(all)'}")

        w("\n")
