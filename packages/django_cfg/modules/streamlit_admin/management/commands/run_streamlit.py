"""
Django management command to run Streamlit server.

Usage:
    python manage.py run_streamlit
    python manage.py run_streamlit --port 8502
    python manage.py run_streamlit --no-reload
"""

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    """Start Streamlit admin server."""

    help = "Start Streamlit admin panel server"

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            "--port",
            type=int,
            help="Port to run on (default: from config)",
        )
        parser.add_argument(
            "--no-reload",
            action="store_true",
            help="Disable auto-reload on file changes",
        )
        parser.add_argument(
            "--background",
            action="store_true",
            help="Run in background",
        )

    def handle(self, *args, **options):
        """Handle command execution."""
        try:
            from django_cfg.modules.streamlit_admin.core import StreamlitRunner
        except ImportError as e:
            raise CommandError(f"Failed to import StreamlitRunner: {e}")

        try:
            runner = StreamlitRunner.from_config()
        except ValueError as e:
            raise CommandError(str(e))
        except FileNotFoundError as e:
            raise CommandError(str(e))

        port = options.get("port")
        reload = not options.get("no_reload", False)
        background = options.get("background", False)

        url = runner.get_url()
        if port:
            url = f"http://localhost:{port}"

        self.stdout.write(
            self.style.SUCCESS(f"\n🚀 Starting Streamlit admin server...")
        )
        self.stdout.write(f"   URL: {url}")
        self.stdout.write(f"   Reload: {'enabled' if reload else 'disabled'}")

        if background:
            self.stdout.write(f"   Mode: background\n")
        else:
            self.stdout.write(f"   Mode: foreground (Ctrl+C to stop)\n")

        try:
            process = runner.start(
                port=port,
                reload=reload,
                background=background,
            )

            if background and process:
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Streamlit started (PID: {process.pid})")
                )
                self.stdout.write(
                    f"   Stop with: kill {process.pid}"
                )

        except RuntimeError as e:
            raise CommandError(str(e))
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("\n\n⚠️  Streamlit stopped"))
