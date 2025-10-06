"""
Django Revolution Management Command

Main command for generating OpenAPI clients.
"""

import sys
import traceback
from django.core.management.base import BaseCommand, CommandError
from django_revolution.cli import main as cli_main


class Command(BaseCommand):
    """Django management command for OpenAPI client generation."""

    help = "Generate OpenAPI clients for API zones using Django Revolution"

    def add_arguments(self, parser):
        """Add command line arguments."""
        # Generation options
        parser.add_argument(
            "--generate", "-g", action="store_true", help="Generate API clients"
        )
        parser.add_argument(
            "--zones",
            "-z",
            nargs="*",
            help="Specific zones to generate (default: all zones)",
        )
        parser.add_argument(
            "--typescript",
            "-t",
            action="store_true",
            help="Generate TypeScript clients only",
        )
        parser.add_argument(
            "--python", "-p", action="store_true", help="Generate Python clients only"
        )
        parser.add_argument(
            "--no-typescript",
            action="store_true",
            help="Skip TypeScript client generation",
        )
        parser.add_argument(
            "--no-python", action="store_true", help="Skip Python client generation"
        )
        parser.add_argument(
            "--no-archive", action="store_true", help="Skip archiving generated clients"
        )
        parser.add_argument(
            "--no-monorepo", action="store_true", help="Skip monorepo sync"
        )
        parser.add_argument(
            "--clean",
            action="store_true",
            help="Clean output directories before generation",
        )
        parser.add_argument(
            "--no-multithreading",
            action="store_true",
            help="Disable multithreaded generation",
        )
        parser.add_argument(
            "--max-workers",
            type=int,
            default=20,
            help="Maximum number of worker threads (default: 20)",
        )

        # Information options
        parser.add_argument(
            "--status",
            action="store_true",
            help="Show current status and configuration",
        )
        parser.add_argument(
            "--list-zones", action="store_true", help="List all available zones"
        )
        parser.add_argument(
            "--validate",
            action="store_true",
            help="Validate environment and configuration",
        )
        parser.add_argument(
            "--show-urls", action="store_true", help="Show URL patterns for each zone"
        )
        parser.add_argument(
            "--validate-zones",
            action="store_true",
            help="Validate each zone with detailed logging",
        )
        parser.add_argument(
            "--test-schemas",
            action="store_true",
            help="Test schema generation for each zone",
        )

        # Utility options
        parser.add_argument(
            "--install-deps", action="store_true", help="Install required dependencies"
        )
        parser.add_argument("--output-dir", help="Override output directory")
        parser.add_argument("--debug", action="store_true", help="Enable debug logging")
        parser.add_argument(
            "--interactive", "-i", action="store_true", help="Run in interactive mode"
        )

    def handle(self, *args, **options):
        """Handle the command execution."""
        try:
            # Convert Django command options to CLI arguments
            # Build argument list for CLI
            cli_args = []

            # Add options as CLI arguments
            if options.get("generate"):
                cli_args.append("--generate")
            if options.get("zones"):
                cli_args.extend(["--zones"] + options["zones"])
            if options.get("typescript"):
                cli_args.append("--typescript")
            if options.get("python"):
                cli_args.append("--python")
            if options.get("no_typescript"):
                cli_args.append("--no-typescript")
            if options.get("no_python"):
                cli_args.append("--no-python")
            if options.get("no_archive"):
                cli_args.append("--no-archive")
            if options.get("no_monorepo"):
                cli_args.append("--no-monorepo")
            if options.get("clean"):
                cli_args.append("--clean")
            if options.get("no_multithreading"):
                cli_args.append("--no-multithreading")
            if options.get("max_workers"):
                cli_args.extend(["--max-workers", str(options["max_workers"])])
            if options.get("status"):
                cli_args.append("--status")
            if options.get("list_zones"):
                cli_args.append("--list-zones")
            if options.get("validate"):
                cli_args.append("--validate")
            if options.get("show_urls"):
                cli_args.append("--show-urls")
            if options.get("validate_zones"):
                cli_args.append("--validate-zones")
            if options.get("test_schemas"):
                cli_args.append("--test-schemas")
            if options.get("install_deps"):
                cli_args.append("--install-deps")
            if options.get("output_dir"):
                cli_args.extend(["--output-dir", options["output_dir"]])
            if options.get("debug"):
                cli_args.append("--debug")
            if options.get("interactive"):
                cli_args.append("--interactive")

            # If no arguments provided, default to interactive mode
            if not cli_args:
                cli_args.append("--interactive")

            # Temporarily replace sys.argv to pass arguments to CLI
            original_argv = sys.argv
            sys.argv = ["django-revolution"] + cli_args

            try:
                # Call CLI main function
                exit_code = cli_main()
                return exit_code
            finally:
                # Restore original sys.argv
                sys.argv = original_argv

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Command failed: {str(e)}"))
            if options.get("debug"):
                self.stdout.write(
                    self.style.ERROR(f"Traceback: {traceback.format_exc()}")
                )
            raise CommandError(f"Generation failed: {str(e)}")
