"""
Django management command for client generation.

Usage:
    python manage.py generate_client --groups cfg custom
    python manage.py generate_client --python
    python manage.py generate_client --interactive
"""


from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    """Generate OpenAPI clients for configured application groups."""

    help = "Generate Python and TypeScript API clients from OpenAPI schemas"

    def add_arguments(self, parser):
        """Add command arguments."""
        # Generation options
        parser.add_argument(
            "--groups",
            nargs="*",
            help="Specific groups to generate (default: all configured groups)",
        )

        parser.add_argument(
            "--python",
            action="store_true",
            help="Generate Python client only",
        )

        parser.add_argument(
            "--typescript",
            action="store_true",
            help="Generate TypeScript client only",
        )

        parser.add_argument(
            "--no-python",
            action="store_true",
            help="Skip Python client generation",
        )

        parser.add_argument(
            "--no-typescript",
            action="store_true",
            help="Skip TypeScript client generation",
        )

        # Utility options
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Dry run - validate configuration but don't generate files",
        )

        parser.add_argument(
            "--list-groups",
            action="store_true",
            help="List configured application groups and exit",
        )

        parser.add_argument(
            "--validate",
            action="store_true",
            help="Validate configuration and exit",
        )

        parser.add_argument(
            "--interactive", "-i",
            action="store_true",
            help="Run in interactive mode",
        )

    def handle(self, *args, **options):
        """Handle command execution."""
        try:
            # Import here to avoid Django import errors
            from django_cfg.modules.django_client.core import get_openapi_service

            # Get service
            service = get_openapi_service()

            if not service.is_enabled():
                raise CommandError(
                    "OpenAPI client generation is not enabled. "
                    "Set 'openapi.enabled = True' in your django-cfg configuration."
                )

            # List groups
            if options["list_groups"]:
                self._list_groups(service)
                return

            # Validate
            if options["validate"]:
                self._validate(service)
                return

            # Interactive mode
            if options["interactive"]:
                self._interactive_mode()
                return

            # Generate clients
            self._generate_clients(service, options)

        except Exception as e:
            raise CommandError(f"Client generation failed: {e}")

    def _list_groups(self, service):
        """List configured groups."""
        groups = service.get_groups()

        if not groups:
            self.stdout.write(self.style.WARNING("No groups configured"))
            return

        self.stdout.write(self.style.SUCCESS(f"\nConfigured groups ({len(groups)}):"))

        for group_name, group_config in groups.items():
            self.stdout.write(f"\n  • {group_name}")
            self.stdout.write(f"    Title: {group_config.title}")
            self.stdout.write(f"    Apps: {len(group_config.apps)} pattern(s)")

            # Show matched apps
            from django.apps import apps

            from django_cfg.modules.django_client.core import GroupManager

            installed_apps = [app.name for app in apps.get_app_configs()]
            manager = GroupManager(service.config, installed_apps, groups=service.get_groups())
            matched_apps = manager.get_group_apps(group_name)

            if matched_apps:
                self.stdout.write(f"    Matched: {len(matched_apps)} app(s)")
                for app in matched_apps[:5]:  # Show first 5
                    self.stdout.write(f"      - {app}")
                if len(matched_apps) > 5:
                    self.stdout.write(f"      ... and {len(matched_apps) - 5} more")
            else:
                self.stdout.write(self.style.WARNING("    Matched: 0 apps"))

    def _validate(self, service):
        """Validate configuration."""
        self.stdout.write("Validating configuration...")

        try:
            service.validate_config()
            self.stdout.write(self.style.SUCCESS("✅ Configuration is valid!"))

            # Show statistics
            from django.apps import apps

            from django_cfg.modules.django_client.core import GroupManager

            installed_apps = [app.name for app in apps.get_app_configs()]
            manager = GroupManager(service.config, installed_apps, groups=service.get_groups())
            stats = manager.get_statistics()

            self.stdout.write("\nStatistics:")
            self.stdout.write(f"  • Total groups: {stats['total_groups']}")
            self.stdout.write(f"  • Total apps in groups: {stats['total_apps_in_groups']}")
            self.stdout.write(f"  • Ungrouped apps: {stats['ungrouped_apps']}")

            if stats["ungrouped_apps"] > 0:
                self.stdout.write(
                    self.style.WARNING(
                        f"\nWarning: {stats['ungrouped_apps']} apps not in any group:"
                    )
                )
                for app in stats["ungrouped_apps_list"][:5]:
                    self.stdout.write(f"  - {app}")
                if len(stats["ungrouped_apps_list"]) > 5:
                    self.stdout.write(f"  ... and {len(stats['ungrouped_apps_list']) - 5} more")

        except Exception as e:
            raise CommandError(f"Validation failed: {e}")

    def _interactive_mode(self):
        """Run interactive mode."""
        try:
            from django_cfg.modules.django_client.core.cli import run_cli
            run_cli()
        except ImportError:
            raise CommandError(
                "Interactive mode requires 'click' package. "
                "Install with: pip install click"
            )

    def _generate_clients(self, service, options):
        """Generate clients."""
        # Determine languages
        if options["python"] and not options["typescript"]:
            python = True
            typescript = False
        elif options["typescript"] and not options["python"]:
            python = False
            typescript = True
        else:
            python = not options["no_python"]
            typescript = not options["no_typescript"]

        # Get groups
        groups = options.get("groups")
        if not groups:
            groups = service.get_group_names()

        if not groups:
            raise CommandError("No groups to generate")

        # Dry run
        dry_run = options["dry_run"]

        if dry_run:
            self.stdout.write(self.style.WARNING("\n🔍 DRY RUN MODE - No files will be generated\n"))

        # Show what will be generated
        self.stdout.write(self.style.SUCCESS(f"Generating clients for {len(groups)} group(s):\n"))

        for group_name in groups:
            group_config = service.get_group(group_name)
            if not group_config:
                self.stdout.write(self.style.WARNING(f"  ⚠️  Group '{group_name}' not found - skipping"))
                continue

            self.stdout.write(f"  • {group_name} ({group_config.title})")

        self.stdout.write("\nLanguages:")
        if python:
            self.stdout.write("  → Python")
        if typescript:
            self.stdout.write("  → TypeScript")

        if dry_run:
            self.stdout.write(self.style.WARNING("\n✅ Dry run completed - no files generated"))
            return

        # Generate clients
        self.stdout.write("\n" + "=" * 60)

        import shutil

        from django.apps import apps
        from drf_spectacular.generators import SchemaGenerator

        from django_cfg.modules.django_client.core import (
            ArchiveManager,
            GroupManager,
            PythonGenerator,
            TypeScriptGenerator,
            parse_openapi,
        )

        # Clean output folders before generation
        schemas_dir = service.config.get_schemas_dir()
        clients_dir = service.config.get_clients_dir()

        if schemas_dir.exists():
            self.stdout.write(f"\n🧹 Cleaning schemas folder: {schemas_dir}")
            shutil.rmtree(schemas_dir)
            schemas_dir.mkdir(parents=True, exist_ok=True)

        if clients_dir.exists():
            self.stdout.write(f"🧹 Cleaning clients folder: {clients_dir}")
            shutil.rmtree(clients_dir)
            clients_dir.mkdir(parents=True, exist_ok=True)

        # Get installed apps (use app.name, not app.label)
        installed_apps = [app.name for app in apps.get_app_configs()]
        manager = GroupManager(service.config, installed_apps, groups=service.get_groups())

        success_count = 0
        error_count = 0

        for group_name in groups:
            group_config = service.get_group(group_name)
            if not group_config:
                continue

            self.stdout.write(f"\n📦 Processing group: {group_name}")

            try:
                # Get apps for this group
                group_apps = manager.get_group_apps(group_name)
                if not group_apps:
                    self.stdout.write(self.style.WARNING(f"  ⚠️  No apps matched for group '{group_name}'"))
                    continue

                self.stdout.write(f"  Apps: {', '.join(group_apps)}")

                # Create dynamic URLconf for this group
                urlconf_module = manager.create_urlconf_module(group_name)

                # Generate OpenAPI schema
                self.stdout.write("  → Generating OpenAPI schema...")

                # Get app labels (not full names) for metadata
                app_labels = []
                for app_name in group_apps:
                    for config in apps.get_app_configs():
                        if config.name == app_name:
                            app_labels.append(config.label)
                            break

                # Temporarily patch SPECTACULAR_SETTINGS to ensure COMPONENT_SPLIT_REQUEST
                from django.conf import settings
                original_settings = getattr(settings, 'SPECTACULAR_SETTINGS', {}).copy()
                patched_settings = original_settings.copy()
                patched_settings['COMPONENT_SPLIT_REQUEST'] = True
                patched_settings['COMPONENT_SPLIT_PATCH'] = True
                settings.SPECTACULAR_SETTINGS = patched_settings

                try:
                    generator = SchemaGenerator(
                        title=group_config.title,
                        description=group_config.description,
                        version=group_config.version,
                        urlconf=urlconf_module,
                    )
                    schema_dict = generator.get_schema(request=None, public=True)
                finally:
                    # Restore original settings
                    settings.SPECTACULAR_SETTINGS = original_settings

                # Add Django metadata to schema (use app labels, not full names)
                schema_dict.setdefault('info', {}).setdefault('x-django-metadata', {
                    'group': group_name,
                    'apps': app_labels,
                    'generator': 'django-client',
                    'generator_version': '1.0.0',
                })

                # Save schema
                schema_path = service.config.get_group_schema_path(group_name)
                schema_path.parent.mkdir(parents=True, exist_ok=True)

                import json
                with open(schema_path, 'w') as f:
                    json.dump(schema_dict, f, indent=2)

                self.stdout.write(f"  ✅ Schema saved: {schema_path}")

                # Parse to IR
                self.stdout.write("  → Parsing to IR...")
                ir_context = parse_openapi(schema_dict)
                self.stdout.write(f"  ✅ Parsed: {len(ir_context.schemas)} schemas, {len(ir_context.operations)} operations")

                # Generate Python client
                if python:
                    self.stdout.write("  → Generating Python client...")
                    python_dir = service.config.get_group_python_dir(group_name)
                    python_dir.mkdir(parents=True, exist_ok=True)

                    py_generator = PythonGenerator(
                        ir_context,
                        client_structure=service.config.client_structure,
                        openapi_schema=schema_dict,
                        tag_prefix=f"{group_name}_",
                        generate_package_files=service.config.generate_package_files,
                    )
                    py_files = py_generator.generate()

                    for generated_file in py_files:
                        full_path = python_dir / generated_file.path
                        full_path.parent.mkdir(parents=True, exist_ok=True)
                        full_path.write_text(generated_file.content)

                    self.stdout.write(f"  ✅ Python client: {python_dir} ({len(py_files)} files)")

                # Generate TypeScript client
                if typescript:
                    self.stdout.write("  → Generating TypeScript client...")
                    ts_dir = service.config.get_group_typescript_dir(group_name)
                    ts_dir.mkdir(parents=True, exist_ok=True)

                    ts_generator = TypeScriptGenerator(
                        ir_context,
                        client_structure=service.config.client_structure,
                        openapi_schema=schema_dict,
                        tag_prefix=f"{group_name}_",
                        generate_package_files=service.config.generate_package_files,
                        generate_zod_schemas=service.config.generate_zod_schemas,
                        generate_fetchers=service.config.generate_fetchers,
                        generate_swr_hooks=service.config.generate_swr_hooks,
                    )
                    ts_files = ts_generator.generate()

                    for generated_file in ts_files:
                        full_path = ts_dir / generated_file.path
                        full_path.parent.mkdir(parents=True, exist_ok=True)
                        full_path.write_text(generated_file.content)

                    self.stdout.write(f"  ✅ TypeScript client: {ts_dir} ({len(ts_files)} files)")

                # Archive if enabled
                if service.config.enable_archive:
                    self.stdout.write("  → Archiving...")
                    archive_manager = ArchiveManager(service.config.get_archive_dir())
                    archive_result = archive_manager.archive_clients(
                        group_name,
                        python_dir=service.config.get_group_python_dir(group_name) if python else None,
                        typescript_dir=service.config.get_group_typescript_dir(group_name) if typescript else None,
                    )
                    if archive_result.get('success'):
                        self.stdout.write(f"  ✅ Archived: {archive_result['archive_path']}")

                success_count += 1

            except Exception as e:
                error_count += 1
                self.stdout.write(self.style.ERROR(f"  ❌ Error: {e}"))
                import traceback
                traceback.print_exc()

        # Summary
        self.stdout.write("\n" + "=" * 60)
        if error_count == 0:
            self.stdout.write(self.style.SUCCESS(f"\n✅ Successfully generated clients for {success_count} group(s)!"))
        else:
            self.stdout.write(self.style.WARNING(f"\n⚠️  Generated {success_count} group(s), {error_count} failed"))

        # Show output paths
        self.stdout.write(f"\nOutput directory: {service.get_output_dir()}")
        if python:
            self.stdout.write(f"  Python:     {service.config.get_python_clients_dir()}")
        if typescript:
            self.stdout.write(f"  TypeScript: {service.config.get_typescript_clients_dir()}")
