"""`python manage.py gen` — Django management wrapper around generation.py.

Loads the user's `generation.py` (defaults to ./generation.py — same dir
as manage.py) and dispatches its `config` to django_generator.run() with
all CLI filters honoured.

Usage:
    python manage.py gen                        # run all targets
    python manage.py gen --ts                   # typescript only
    python manage.py gen --py                   # python only
    python manage.py gen --target packages      # only TargetType.PACKAGES
    python manage.py gen --groups cfg_accounts  # filter by group name(s)
    python manage.py gen --dry-run              # plan without writes
    python manage.py gen --list-targets         # show targets summary
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Generate API clients from generation.py config (django_generator)."

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument(
            "--config",
            default="generation.py",
            help="Path to generation.py (default: ./generation.py).",
        )
        # Language filters
        parser.add_argument("--ts", action="store_true", help="TypeScript only")
        parser.add_argument("--py", action="store_true", help="Python only")
        parser.add_argument("--go", action="store_true", help="Go only")
        parser.add_argument("--swift", action="store_true", help="Swift only")
        # Target / group filters
        parser.add_argument(
            "--target", "-t", type=str, default=None,
            help="Target type filter: admin, web, packages, sdk, parsers, extensions",
        )
        parser.add_argument(
            "--groups", nargs="+", default=None,
            help="Specific group names to run.",
        )
        # Behaviour
        parser.add_argument("--dry-run", action="store_true", help="Plan without writes.")
        parser.add_argument("--list-targets", action="store_true",
                            help="Show configured targets and exit.")
        parser.add_argument("--verbose", action="store_true")
        parser.add_argument("--quiet", action="store_true")

    def handle(self, *args: Any, **opts: Any) -> None:
        config_path = Path(opts["config"]).resolve()
        if not config_path.is_file():
            raise CommandError(f"config not found: {config_path}")

        gen_module = _load_module(config_path)
        cfg_obj = getattr(gen_module, "config", None)
        if cfg_obj is None:
            raise CommandError("generation.py must export `config` (Config object).")

        if opts["list_targets"]:
            from django_cfg.modules.django_generator import inspect_config
            summary = inspect_config(cfg_obj)
            for t in summary.openapi or []:
                self.stdout.write(f"  [{t.lang}] [{t.type}] {t.path}")
                self.stdout.write(f"           groups: {', '.join(t.groups)}")
            return

        # Translate flags → run() kwargs
        lang_map = {"ts": "typescript", "py": "python", "go": "go", "swift": "swift"}
        only_platforms = [v for k, v in lang_map.items() if opts.get(k)] or None

        from django_cfg.modules.django_generator import run

        logger = run(
            cfg_obj,
            only_platforms=only_platforms,
            only_target=opts.get("target"),
            only_groups=opts.get("groups"),
            dry_run=opts.get("dry_run", False),
            verbose=opts.get("verbose", False),
            quiet=opts.get("quiet", False),
        )

        if logger.stats.errors:
            raise CommandError(
                f"{len(logger.stats.errors)} target(s) failed."
            )


def _load_module(path: Path):
    spec = importlib.util.spec_from_file_location(
        "_django_generator_user_config", path,
    )
    if spec is None or spec.loader is None:
        raise CommandError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
