"""
Django management command for client generation.

Usage:
    python manage.py generate_client --groups cfg custom
    python manage.py generate_client --python
    python manage.py generate_client --swift
    python manage.py generate_client --interactive
"""

from django.core.management.base import CommandError

from django_cfg.management.utils import AdminCommand


class Command(AdminCommand):
    """Generate OpenAPI clients for configured application groups."""

    command_name = 'generate_client'
    help = "Generate Python, TypeScript, Go, Swift, and Proto API clients from OpenAPI schemas"

    def add_arguments(self, parser):
        """Add command arguments."""
        # Language selection
        lang_group = parser.add_argument_group('Language Selection')

        lang_group.add_argument(
            "--python",
            action="store_true",
            help="Generate Python client only",
        )
        lang_group.add_argument(
            "--typescript",
            action="store_true",
            help="Generate TypeScript client only",
        )
        lang_group.add_argument(
            "--go",
            action="store_true",
            help="Generate Go client only",
        )
        lang_group.add_argument(
            "--proto",
            action="store_true",
            help="Generate Protocol Buffer/gRPC definitions only",
        )
        lang_group.add_argument(
            "--swift",
            action="store_true",
            help="Generate Swift client (uses apple/swift-openapi-generator)",
        )
        lang_group.add_argument(
            "--swift-codable",
            action="store_true",
            dest="swift_codable",
            help="Generate simple Swift Codable types (no OpenAPIRuntime dependency)",
        )

        # Skip languages
        skip_group = parser.add_argument_group('Skip Languages')

        skip_group.add_argument(
            "--no-python",
            action="store_true",
            help="Skip Python client generation",
        )
        skip_group.add_argument(
            "--no-typescript",
            action="store_true",
            help="Skip TypeScript client generation",
        )
        skip_group.add_argument(
            "--no-go",
            action="store_true",
            help="Skip Go client generation",
        )
        skip_group.add_argument(
            "--no-proto",
            action="store_true",
            help="Skip Protocol Buffer generation",
        )

        # External generators
        ext_group = parser.add_argument_group('External Generators')

        ext_group.add_argument(
            "--external-go",
            action="store_true",
            help="Use oapi-codegen instead of built-in Go generator",
        )
        ext_group.add_argument(
            "--external-python",
            action="store_true",
            help="Use openapi-python-client instead of built-in Python generator",
        )
        ext_group.add_argument(
            "--check-external",
            action="store_true",
            help="Check which external generators are installed",
        )

        # Groups
        parser.add_argument(
            "--groups",
            nargs="*",
            help="Specific groups to generate (default: all configured groups)",
        )

        # Utility options
        util_group = parser.add_argument_group('Utility Options')

        util_group.add_argument(
            "--no-build",
            action="store_true",
            help="Skip Next.js admin build",
        )
        util_group.add_argument(
            "--dry-run",
            action="store_true",
            help="Dry run - validate configuration but don't generate files",
        )
        util_group.add_argument(
            "--list-groups",
            action="store_true",
            help="List configured application groups and exit",
        )
        util_group.add_argument(
            "--validate",
            action="store_true",
            help="Validate configuration and exit",
        )
        util_group.add_argument(
            "--interactive", "-i",
            action="store_true",
            help="Run in interactive mode",
        )
        util_group.add_argument(
            "--copy-cfg-clients",
            action="store_true",
            help="Copy cfg_* API clients to Next.js admin",
        )
        util_group.add_argument(
            "--skip-nextjs-copy",
            action="store_true",
            help="Skip copying clients to Next.js admin project",
        )
        util_group.add_argument(
            "--verbose",
            action="store_true",
            help="Show detailed error messages with full tracebacks",
        )

    def handle(self, *args, **options):
        """Handle command execution."""
        try:
            from django_cfg.modules.django_client.core import get_openapi_service

            service = get_openapi_service()

            if not service.is_enabled():
                raise CommandError(
                    "OpenAPI client generation is not enabled. "
                    "Set 'openapi.enabled = True' in your django-cfg configuration."
                )

            # Check external generators
            if options.get("check_external"):
                self._check_external_generators()
                return

            # List groups
            if options.get("list_groups"):
                self._list_groups(service)
                return

            # Validate
            if options.get("validate"):
                self._validate(service)
                return

            # Interactive mode
            if options.get("interactive"):
                self._interactive_mode()
                return

            # Generate clients
            self._generate_clients(service, options)

        except Exception as e:
            import traceback
            tb_str = traceback.format_exc()
            self.stderr.write(self.style.ERROR(f"\nTraceback:\n{tb_str}"))
            raise CommandError(f"Client generation failed: {e}")

    def _check_external_generators(self):
        """Check which external generators are installed."""
        from django_cfg.modules.django_client.core.external import (
            check_all_installations,
            get_install_instructions,
            GeneratorLanguage,
        )

        self.stdout.write("\n🔍 Checking external generators...\n")

        status = check_all_installations()

        for lang, installed in status.items():
            if installed:
                self.stdout.write(self.style.SUCCESS(f"  ✅ {lang.value}: installed"))
            else:
                self.stdout.write(self.style.WARNING(f"  ❌ {lang.value}: not installed"))
                self.stdout.write(f"\n{get_install_instructions(lang)}")

    def _list_groups(self, service):
        """List configured groups."""
        from django.apps import apps
        from django_cfg.modules.django_client.core import GroupManager

        groups = service.get_groups()

        if not groups:
            self.stdout.write(self.style.WARNING("No groups configured"))
            return

        self.stdout.write(self.style.SUCCESS(f"\nConfigured groups ({len(groups)}):"))

        installed_apps = [app.name for app in apps.get_app_configs()]
        manager = GroupManager(service.config, installed_apps, groups=groups)

        for group_name, group_config in groups.items():
            self.stdout.write(f"\n  • {group_name}")
            self.stdout.write(f"    Title: {group_config.title}")
            self.stdout.write(f"    Apps: {len(group_config.apps)} pattern(s)")

            matched_apps = manager.get_group_apps(group_name)
            if matched_apps:
                self.stdout.write(f"    Matched: {len(matched_apps)} app(s)")
                for app in matched_apps[:5]:
                    self.stdout.write(f"      - {app}")
                if len(matched_apps) > 5:
                    self.stdout.write(f"      ... and {len(matched_apps) - 5} more")
            else:
                self.stdout.write(self.style.WARNING("    Matched: 0 apps"))

    def _validate(self, service):
        """Validate configuration."""
        from django.apps import apps
        from django_cfg.modules.django_client.core import GroupManager

        self.stdout.write("Validating configuration...")

        try:
            service.validate_config()
            self.stdout.write(self.style.SUCCESS("✅ Configuration is valid!"))

            installed_apps = [app.name for app in apps.get_app_configs()]
            manager = GroupManager(service.config, installed_apps, groups=service.get_groups())
            stats = manager.get_statistics()

            self.stdout.write("\nStatistics:")
            self.stdout.write(f"  • Total groups: {stats['total_groups']}")
            self.stdout.write(f"  • Total apps: {stats['total_apps_in_groups']}")
            self.stdout.write(f"  • Ungrouped: {stats['ungrouped_apps']}")

        except Exception as e:
            raise CommandError(f"Validation failed: {e}")

    def _interactive_mode(self):
        """Run interactive mode."""
        try:
            from django_cfg.modules.django_client.core.cli import run_cli
            run_cli()
        except ImportError:
            raise CommandError("Interactive mode requires 'click' package.")

    def _generate_clients(self, service, options):
        """Generate clients using the orchestrator."""
        from django_cfg.modules.django_client.generate_client import (
            GenerationConfig,
            ClientGenerationOrchestrator,
        )

        # Create config from options
        config = GenerationConfig.from_options(options, service.config)

        # Create orchestrator with styled logging
        orchestrator = ClientGenerationOrchestrator(
            service=service,
            config=config,
            log=lambda msg: self.stdout.write(msg),
            log_success=lambda msg: self.stdout.write(self.style.SUCCESS(msg)),
            log_warning=lambda msg: self.stdout.write(self.style.WARNING(msg)),
            log_error=lambda msg: self.stdout.write(self.style.ERROR(msg)),
        )

        # Generate all
        results = orchestrator.generate_all()

        # Check for failures
        failures = [r for r in results if not r.success and r.error]
        if failures:
            for r in failures:
                self.stdout.write(self.style.ERROR(f"  {r.group_name}: {r.error}"))
