"""
Django CFG Editable-Install Checker

Diagnoses the common dev gotcha where an editable install of django-cfg is
silently replaced by the PyPI copy in site-packages (e.g. after `uv sync`).

Prints the actual ``django_cfg.__file__`` location and complains loudly (and
exits non-zero) if it resolves into site-packages while a local editable source
was expected. Safe to run anywhere — read-only, never mutates anything.
"""

from django.core.management.base import BaseCommand

from django_cfg.core.integration.editable_check import (
    EDITABLE_MARKER_ENV,
    get_editable_status,
)


class Command(BaseCommand):
    """Report where django_cfg is actually loaded from (editable vs PyPI)."""

    help = "Check whether django-cfg is loaded from your editable source or the PyPI copy"

    def add_arguments(self, parser):
        parser.add_argument(
            "--strict",
            action="store_true",
            help="Exit with code 1 if the PyPI copy is loaded instead of editable source",
        )

    def handle(self, *args, **options):
        status = get_editable_status()

        self.stdout.write(self.style.SUCCESS("\n🧩 Django CFG Editable Check\n"))

        self.stdout.write(f"  📂 Loaded from:      {status.loaded_path or 'unknown'}")
        self.stdout.write(
            f"  📦 In site-packages: {'yes' if status.is_site_packages else 'no'}"
        )
        self.stdout.write(
            f"  🔗 Editable source:  {status.expected_source or 'not found (~/djangocfg)'}"
        )
        self.stdout.write(
            f"  🚩 Editable env:     {EDITABLE_MARKER_ENV}"
            f" {'set' if status.editable_expected and status.expected_source is None else ''}"
        )
        self.stdout.write(
            f"  🎯 Editable expected: {'yes' if status.editable_expected else 'no'}\n"
        )

        if status.mismatch:
            self.stdout.write(
                self.style.ERROR(
                    "❌ django-cfg loaded from PyPI copy (site-packages), not your editable source."
                )
            )
            self.stdout.write(
                self.style.WARNING(
                    "   A `uv sync` / `uv run` likely reinstalled the PyPI copy over your editable link."
                )
            )
            self.stdout.write(
                self.style.WARNING("   Fix: make install-local\n")
            )
            if options.get("strict"):
                raise SystemExit(1)
            return

        if not status.editable_expected:
            self.stdout.write(
                "ℹ️  No editable install expected on this machine (no ~/djangocfg, no env marker)."
            )
            self.stdout.write("   Loading from PyPI is fine here.\n")
            return

        self.stdout.write(
            self.style.SUCCESS("✅ django-cfg is loaded from your editable source.\n")
        )
