"""
Generate Python API clients for Streamlit admin.

Runs full Python client generation + copies "cfg" package
to streamlit_admin/api/generated/.

Usage:
    python manage.py gen_streamlit
    python manage.py gen_streamlit --copy-only
"""

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    """Generate Python API clients for Streamlit admin."""

    help = "Generate Python API clients and copy to Streamlit admin"

    def add_arguments(self, parser):
        parser.add_argument(
            "--copy-only",
            action="store_true",
            help="Only copy existing clients (skip generation)",
        )

    def handle(self, *args, **options):
        copy_only = options["copy_only"]

        if not copy_only:
            self.stdout.write("Generating Python API clients...")
            from django.core.management import call_command

            try:
                call_command("generate_client", python=True, verbosity=0)
            except Exception as e:
                raise CommandError(f"Client generation failed: {e}")

            self.stdout.write(self.style.SUCCESS("Python clients generated"))

        self.stdout.write("Copying clients to Streamlit...")
        from django_cfg.modules.streamlit_admin.core import StreamlitClientCopier

        try:
            copier = StreamlitClientCopier()
            stats = copier.copy()
        except FileNotFoundError as e:
            raise CommandError(str(e))

        packages = ", ".join(stats["copied_packages"]) or "none"
        self.stdout.write(
            self.style.SUCCESS(
                f"Copied to Streamlit: {packages}\n"
                f"Target: {stats['target_path']}"
            )
        )
