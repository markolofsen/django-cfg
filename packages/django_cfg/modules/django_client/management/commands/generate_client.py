"""
Django management command for client generation.

Usage:
    python manage.py generate_client --groups cfg custom
    python manage.py generate_client --python
    python manage.py generate_client --interactive
"""


from django.core.management.base import CommandError

from django_cfg.management.utils import AdminCommand


class Command(AdminCommand):
    """Generate OpenAPI clients for configured application groups."""

    command_name = 'generate_client'
    help = "Generate Python, TypeScript, and Go API clients from OpenAPI schemas"

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
            "--go",
            action="store_true",
            help="Generate Go client only",
        )

        parser.add_argument(
            "--proto",
            action="store_true",
            help="Generate Protocol Buffer/gRPC definitions only",
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

        parser.add_argument(
            "--no-go",
            action="store_true",
            help="Skip Go client generation",
        )

        parser.add_argument(
            "--no-proto",
            action="store_true",
            help="Skip Protocol Buffer generation",
        )

        # Utility options
        parser.add_argument(
            "--no-build",
            action="store_true",
            help="Skip Next.js admin build (useful when calling from Makefile)",
        )

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
        if options["python"] and not options["typescript"] and not options["go"] and not options["proto"]:
            python = True
            typescript = False
            go = False
            proto = False
        elif options["typescript"] and not options["python"] and not options["go"] and not options["proto"]:
            python = False
            typescript = True
            go = False
            proto = False
        elif options["go"] and not options["python"] and not options["typescript"] and not options["proto"]:
            python = False
            typescript = False
            go = True
            proto = False
        elif options["proto"] and not options["python"] and not options["typescript"] and not options["go"]:
            python = False
            typescript = False
            go = False
            proto = True
        else:
            python = not options["no_python"]
            typescript = not options["no_typescript"]
            go = not options["no_go"]
            proto = not options["no_proto"]

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
        if go:
            self.stdout.write("  → Go")
        if proto:
            self.stdout.write("  → Protocol Buffers (proto3)")

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
            GoGenerator,
            GroupManager,
            ProtoGenerator,
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

                # Generate Go client
                if go:
                    self.stdout.write("  → Generating Go client...")
                    go_dir = service.config.get_group_go_dir(group_name)
                    go_dir.mkdir(parents=True, exist_ok=True)

                    go_generator = GoGenerator(
                        ir_context,
                        client_structure=service.config.client_structure,
                        openapi_schema=schema_dict,
                        tag_prefix=f"{group_name}_",
                        generate_package_files=service.config.generate_package_files,
                        package_config={
                            "name": group_name,
                            "module_name": group_name,
                            "version": "v1.0.0",
                        },
                    )
                    go_files = go_generator.generate()

                    for generated_file in go_files:
                        full_path = go_dir / generated_file.path
                        full_path.parent.mkdir(parents=True, exist_ok=True)
                        full_path.write_text(generated_file.content)

                    self.stdout.write(f"  ✅ Go client: {go_dir} ({len(go_files)} files)")

                # Generate Proto files
                if proto:
                    self.stdout.write("  → Generating Protocol Buffer definitions...")
                    proto_dir = clients_dir / "proto" / group_name
                    proto_dir.mkdir(parents=True, exist_ok=True)

                    proto_generator = ProtoGenerator(
                        ir_context,
                        split_files=True,  # Generate separate messages.proto and services.proto
                        package_name=f"{group_name}.v1",
                    )
                    proto_files = proto_generator.generate()

                    for generated_file in proto_files:
                        full_path = proto_dir / generated_file.path
                        full_path.parent.mkdir(parents=True, exist_ok=True)
                        full_path.write_text(generated_file.content)

                    self.stdout.write(f"  ✅ Proto files: {proto_dir} ({len(proto_files)} files)")

                # Archive if enabled
                if service.config.enable_archive:
                    self.stdout.write("  → Archiving...")
                    archive_manager = ArchiveManager(service.config.get_archive_dir())
                    archive_result = archive_manager.archive_clients(
                        group_name,
                        python_dir=service.config.get_group_python_dir(group_name) if python else None,
                        typescript_dir=service.config.get_group_typescript_dir(group_name) if typescript else None,
                        go_dir=go_dir if go else None,
                        proto_dir=proto_dir if proto else None,
                    )
                    if archive_result.get('success'):
                        self.stdout.write(f"  ✅ Archived: {archive_result['archive_path']}")

                success_count += 1

            except Exception as e:
                error_count += 1
                self.stdout.write(self.style.ERROR(f"  ❌ Error: {e}"))
                import traceback
                traceback.print_exc()

        # Build and copy to Next.js admin (if configured)
        if typescript and success_count > 0:
            # First copy API clients
            self._copy_to_nextjs_admin(service)
            # Then build Next.js (so clients are included in build)
            # Skip build if --no-build flag is set
            if not options.get("no_build"):
                self._build_nextjs_admin()
            else:
                self.stdout.write(self.style.WARNING(
                    "\n⏭️  Skipping Next.js build (--no-build flag set)"
                ))

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
        if go:
            self.stdout.write(f"  Go:         {service.config.get_go_clients_dir()}")

    def _copy_to_nextjs_admin(self, service):
        """Copy TypeScript clients to Next.js admin project (if configured)."""
        try:
            from django_cfg.core.config import get_current_config
            from pathlib import Path
            import shutil

            config = get_current_config()
            if not config or not config.nextjs_admin:
                return

            nextjs_config = config.nextjs_admin
            if not nextjs_config.auto_copy_api:
                return

            # Resolve Next.js project path
            base_dir = config.base_dir
            project_path = Path(nextjs_config.project_path)
            if not project_path.is_absolute():
                project_path = base_dir / project_path

            if not project_path.exists():
                self.stdout.write(self.style.WARNING(
                    f"\n⚠️  Next.js project not found: {project_path}"
                ))
                return

            # Resolve API output path
            api_output_path = project_path / nextjs_config.get_api_output_path()

            # Source: TypeScript clients directory
            ts_source = service.config.get_typescript_clients_dir()

            if not ts_source.exists():
                return

            self.stdout.write(f"\n📦 Copying TypeScript clients to Next.js admin...")

            # Clean api_output_path before copying (remove old generated files)
            if api_output_path.exists():
                self.stdout.write(f"  🧹 Cleaning API output directory: {api_output_path.relative_to(project_path)}")
                shutil.rmtree(api_output_path)

            # Recreate directory
            api_output_path.mkdir(parents=True, exist_ok=True)

            # Copy each group (exclude 'cfg' for Next.js admin)
            copied_count = 0
            for group_dir in ts_source.iterdir():
                if not group_dir.is_dir():
                    continue

                group_name = group_dir.name

                # Skip 'cfg' group for Next.js admin
                if group_name == 'cfg':
                    self.stdout.write(f"  ⏭️  Skipping 'cfg' group (excluded from Next.js admin)")
                    continue

                target_dir = api_output_path / group_name

                # Copy group directory
                shutil.copytree(group_dir, target_dir)
                copied_count += 1

                self.stdout.write(f"  ✅ {group_name} → {target_dir.relative_to(project_path)}")

            if copied_count > 0:
                self.stdout.write(self.style.SUCCESS(
                    f"\n✅ Copied {copied_count} group(s) to Next.js admin!"
                ))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n❌ Failed to copy to Next.js admin: {e}"))
            import traceback
            traceback.print_exc()

    def _build_nextjs_admin(self):
        """Build Next.js admin static export (if configured)."""
        try:
            from django_cfg.core.config import get_current_config
            from pathlib import Path
            import subprocess
            import shutil

            config = get_current_config()
            if not config or not config.nextjs_admin:
                return

            nextjs_config = config.nextjs_admin
            if not nextjs_config.auto_build:
                return

            # Resolve Next.js project path
            base_dir = config.base_dir
            project_path = Path(nextjs_config.project_path)
            if not project_path.is_absolute():
                project_path = base_dir / project_path

            if not project_path.exists():
                self.stdout.write(self.style.WARNING(
                    f"\n⚠️  Next.js project not found: {project_path}"
                ))
                return

            self.stdout.write(f"\n🏗️  Building Next.js admin static export...")

            # Check if pnpm is available
            pnpm_path = shutil.which('pnpm')
            if not pnpm_path:
                self.stdout.write(self.style.WARNING(
                    "\n⚠️  pnpm not found. Skipping Next.js build."
                ))
                self.stdout.write("   Install pnpm or set auto_build=False in NextJsAdminConfig")
                return

            # Run pnpm build with NEXT_PUBLIC_STATIC_BUILD=true for static export
            try:
                import os
                env = os.environ.copy()
                env['NEXT_PUBLIC_STATIC_BUILD'] = 'true'

                result = subprocess.run(
                    [pnpm_path, 'build'],
                    cwd=str(project_path),
                    capture_output=True,
                    text=True,
                    timeout=300,  # 5 minutes timeout
                    env=env,
                )

                if result.returncode == 0:
                    self.stdout.write(self.style.SUCCESS(
                        f"\n✅ Next.js admin built successfully!"
                    ))

                    # Check build output
                    static_output = project_path / nextjs_config.get_static_output_path()
                    if static_output.exists():
                        self.stdout.write(self.style.SUCCESS(
                            f"   📁 Build output: {static_output.relative_to(base_dir)}"
                        ))

                        # Create ZIP archive for Django static (Docker-ready)
                        # Use solution project's BASE_DIR from Django settings
                        from django.conf import settings as django_settings
                        solution_base_dir = django_settings.BASE_DIR

                        django_static_zip = nextjs_config.get_static_zip_path(solution_base_dir)

                        try:
                            # Ensure static directory exists
                            django_static_zip.parent.mkdir(parents=True, exist_ok=True)

                            # Remove old ZIP if exists
                            if django_static_zip.exists():
                                django_static_zip.unlink()

                            # Check if zip command is available
                            zip_path = shutil.which('zip')
                            if not zip_path:
                                self.stdout.write(self.style.WARNING(
                                    "   ⚠️  zip command not found. Falling back to Python zipfile..."
                                ))
                                # Fallback to Python zipfile
                                import zipfile
                                with zipfile.ZipFile(django_static_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
                                    for file_path in static_output.rglob('*'):
                                        if file_path.is_file():
                                            arcname = file_path.relative_to(static_output)
                                            zipf.write(file_path, arcname)
                            else:
                                # Use system zip command (faster)
                                subprocess.run(
                                    [zip_path, '-r', '-q', str(django_static_zip), '.'],
                                    cwd=str(static_output),
                                    check=True
                                )

                            # Get ZIP size
                            zip_size_mb = django_static_zip.stat().st_size / (1024 * 1024)

                            # Show relative path from solution BASE_DIR
                            relative_zip_path = django_static_zip.relative_to(solution_base_dir)

                            self.stdout.write(self.style.SUCCESS(
                                f"   ✅ Created ZIP archive: {relative_zip_path} ({zip_size_mb:.1f}MB)"
                            ))
                            self.stdout.write(self.style.SUCCESS(
                                f"   📍 ZIP location: {django_static_zip}"
                            ))
                            self.stdout.write(self.style.SUCCESS(
                                "   ℹ️  This ZIP is used by NextJsAdminView (Tab 2: External Admin)"
                            ))

                        except Exception as zip_error:
                            self.stdout.write(self.style.ERROR(
                                f"   ❌ Failed to create ZIP archive: {zip_error}"
                            ))
                    else:
                        self.stdout.write(self.style.WARNING(
                            f"   ⚠️  Build output not found at: {static_output.relative_to(base_dir)}"
                        ))
                else:
                    self.stdout.write(self.style.ERROR(
                        f"\n❌ Next.js build failed with exit code {result.returncode}"
                    ))

                    # Show full error output
                    if result.stderr:
                        self.stdout.write(self.style.ERROR(f"\n   stderr:\n{result.stderr}"))
                    if result.stdout:
                        self.stdout.write(self.style.ERROR(f"\n   stdout:\n{result.stdout}"))

                    # Exit on build failure
                    raise CommandError(
                        f"Next.js build failed with exit code {result.returncode}. "
                        "Fix the build errors and try again."
                    )

            except subprocess.TimeoutExpired:
                self.stdout.write(self.style.ERROR(
                    "\n❌ Next.js build timed out (5 minutes)"
                ))
                raise CommandError("Next.js build timed out after 5 minutes")

            except Exception as build_error:
                self.stdout.write(self.style.ERROR(
                    f"\n❌ Build command failed: {build_error}"
                ))
                raise CommandError(f"Next.js build command failed: {build_error}")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n❌ Failed to build Next.js admin: {e}"))
            import traceback
            traceback.print_exc()
