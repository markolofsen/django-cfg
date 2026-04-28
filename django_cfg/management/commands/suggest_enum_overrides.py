"""Print a working ``ENUM_NAME_OVERRIDES`` dict for every enum that
drf-spectacular currently mangles with a hash suffix.

Thin wrapper around
``django_cfg.modules.django_generator.openapi.spectacular.suggest_enum_overrides``
— the real resolution logic lives in that service so the same code is
shared with the postprocessing hook.

Usage::

    python manage.py suggest_enum_overrides
    python manage.py suggest_enum_overrides --json
"""

from __future__ import annotations

import json

from django.core.management.base import BaseCommand, CommandError

from django_cfg.modules.django_generator.openapi.spectacular import (
    suggest_enum_overrides,
)


class Command(BaseCommand):
    help = "Suggest ENUM_NAME_OVERRIDES entries for hash-suffixed enums."

    def add_arguments(self, parser):
        parser.add_argument(
            "--json",
            action="store_true",
            help="Emit suggestions as JSON instead of Python literal.",
        )

    def handle(self, *args, **options):
        try:
            result = suggest_enum_overrides()
        except ImportError as exc:  # pragma: no cover
            raise CommandError(
                "drf-spectacular is not installed in this environment."
            ) from exc

        if result.is_empty:
            self.stdout.write(self.style.SUCCESS("No enum collisions detected."))
            return

        if options.get("json"):
            self.stdout.write(json.dumps(result.as_dict(), indent=2))
            return

        self.stdout.write("# Add to SpectacularConfig.enum_name_overrides:")
        self.stdout.write("ENUM_NAME_OVERRIDES = {")
        for line in result.render_python_dict():
            self.stdout.write(line)
        self.stdout.write("}")

        if result.ambiguous:
            self.stdout.write("")
            self.stdout.write(
                "# ⚠ Multiple TextChoices classes matched these enums — "
                "review and pin the right one:"
            )
            for name, paths in result.ambiguous:
                self.stdout.write(f"#   {name}: {paths}")
