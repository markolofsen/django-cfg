"""
Unified client generation command.

v5.3: Groups only in Target, no inheritance.

Usage:
    python manage.py gen                        # all targets, all languages
    python manage.py gen --ts                   # typescript only
    python manage.py gen --target admin         # specific target
    python manage.py gen --ts --target admin    # combined
    python manage.py gen --groups profiles      # specific groups
    python manage.py gen --list-targets         # show configured targets
    python manage.py gen --dry-run              # preview
"""

from django.core.management.base import BaseCommand

from django_cfg.modules.django_codegen import run
from django_cfg.modules.django_codegen.config import (
    Config,
    TargetType,
)


class Command(BaseCommand):
    help = "Generate API clients based on generation.py config"

    def add_arguments(self, parser):
        # Language filters
        parser.add_argument("--ts", action="store_true", help="TypeScript only")
        parser.add_argument("--py", action="store_true", help="Python only")
        parser.add_argument("--go", action="store_true", help="Go only")
        parser.add_argument("--swift", action="store_true", help="Swift only")

        # Target filter
        parser.add_argument(
            "--target",
            "-t",
            type=str,
            help="Target type: admin, packages, extensions, parsers, sdk, web, orm",
        )

        # Group filter
        parser.add_argument("--groups", nargs="+", help="Specific groups only")

        # Dry run
        parser.add_argument("--dry-run", action="store_true", help="Preview without changes")

        # List targets
        parser.add_argument(
            "--list-targets",
            action="store_true",
            help="List all configured targets",
        )

    def handle(self, *args, **options):
        # Load config from project's generation.py
        try:
            from generation import config
        except ImportError:
            self.stderr.write(
                self.style.ERROR(
                    "No generation.py found in project root.\n"
                    "Create generation.py with your Config definition."
                )
            )
            return

        # List targets mode
        if options.get("list_targets"):
            self._list_targets(config)
            return

        # Determine language filter
        langs = []
        if options["ts"]:
            langs.append("typescript")
        if options["py"]:
            langs.append("python")
        if options["go"]:
            langs.append("go")
        if options["swift"]:
            langs.append("swift")

        # None means all platforms
        only_platforms = langs if langs else None

        # Run with rich logging
        result = run(
            config,
            only_platforms=only_platforms,
            only_target=options.get("target"),
            only_groups=options.get("groups"),
            dry_run=options.get("dry_run", False),
            verbose=options.get("verbose", False),
        )

        # Log any errors to Django stderr
        if result.stats.errors:
            for error in result.stats.errors:
                self.stderr.write(self.style.ERROR(error))

    def _list_targets(self, config: Config) -> None:
        """List all configured targets."""
        self.stdout.write("\nConfigured targets:\n")

        if config.openapi:
            openapi = config.openapi

            # Check if using legacy format
            if openapi.is_legacy_format():
                self.stdout.write("  (Legacy format)\n")
                for lang in ["typescript", "python", "go", "swift"]:
                    groups = getattr(openapi, lang, [])
                    if groups and lang in openapi.legacy_targets:
                        self.stdout.write(f"\n  {lang}:")
                        self.stdout.write(f"    [default] {openapi.legacy_targets[lang]}")
                        self.stdout.write(f"         groups: {', '.join(groups)}")
            else:
                # New format - group targets by language
                by_lang: dict = {}
                for target in openapi.targets:
                    lang_val = target.lang.value
                    if lang_val not in by_lang:
                        by_lang[lang_val] = []
                    by_lang[lang_val].append(target)

                for lang_val, targets in by_lang.items():
                    self.stdout.write(f"\n  {lang_val}:")
                    for target in targets:
                        t = target.type.value if isinstance(target.type, TargetType) else target.type
                        self.stdout.write(f"    [{t}] {target.path}")
                        self.stdout.write(f"         groups: {', '.join(target.groups)}")
                        if target.post_build:
                            self.stdout.write(f"         post_build: {target.post_build}")

                # Show auto-discovered extensions
                if openapi.extensions:
                    ext = openapi.extensions
                    discovered = ext.discover()
                    if discovered:
                        self.stdout.write(f"\n  extensions (auto-discovered from {ext.frontend_path}):")
                        for target in discovered:
                            self.stdout.write(f"    [{target.groups[0]}] {target.path}")
                            if target.post_build:
                                self.stdout.write(f"         post_build: {target.post_build}")
                    else:
                        self.stdout.write(f"\n  extensions (none found in {ext.frontend_path})")

        if config.centrifugo:
            self.stdout.write("\n\nCentrifugo:")
            if config.centrifugo.is_legacy_format():
                for lang in ["typescript", "swift", "go"]:
                    groups = getattr(config.centrifugo, lang, [])
                    if groups and lang in config.centrifugo.legacy_targets:
                        self.stdout.write(f"\n  {lang}:")
                        self.stdout.write(f"    {config.centrifugo.legacy_targets[lang]}")
                        self.stdout.write(f"         groups: {', '.join(groups)}")
            else:
                for target in config.centrifugo.targets:
                    t = target.type.value if isinstance(target.type, TargetType) else target.type
                    self.stdout.write(f"\n  {target.lang.value}:")
                    self.stdout.write(f"    [{t}] {target.path}")
                    self.stdout.write(f"         groups: {', '.join(target.groups)}")

        if config.sdk:
            self.stdout.write("\n\nSDK Packages:")
            for pkg in config.sdk.packages:
                self.stdout.write(f"\n  {pkg.name}:")
                self.stdout.write(f"    platform: {pkg.platform.value}")
                self.stdout.write(f"    target: {pkg.target}")
                self.stdout.write(f"    groups: {', '.join(pkg.groups)}")

        if config.orm:
            self.stdout.write("\n\nORM (FastAPI/SQLModel):")
            for target in config.orm.targets:
                gen = target.generator.value if hasattr(target.generator, 'value') else target.generator
                self.stdout.write(f"\n  [{gen}] {target.output}")
                if target.apps:
                    self.stdout.write(f"         apps: {', '.join(target.apps)}")
                else:
                    self.stdout.write("         apps: (all)")

        self.stdout.write("\n")
