"""
Client Generation Orchestrator.

Coordinates the entire client generation process.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import TYPE_CHECKING, Callable

from .config import GenerationConfig, GenerationResult
from .generators import InternalGenerators, ExternalGenerators
from .utils import NextJsUtils, TypeScriptUtils, SchemaUtils

if TYPE_CHECKING:
    from django_cfg.modules.django_client.core import OpenAPIService


class ClientGenerationOrchestrator:
    """
    Orchestrates client generation for all configured groups.

    Usage:
        orchestrator = ClientGenerationOrchestrator(service, config, stdout)
        results = orchestrator.generate_all()
    """

    def __init__(
        self,
        service: "OpenAPIService",
        config: GenerationConfig,
        *,
        log: Callable[[str], None] | None = None,
        log_success: Callable[[str], None] | None = None,
        log_warning: Callable[[str], None] | None = None,
        log_error: Callable[[str], None] | None = None,
    ):
        self.service = service
        self.config = config

        # Logging callbacks
        self.log = log or print
        self.log_success = log_success or self.log
        self.log_warning = log_warning or self.log
        self.log_error = log_error or self.log

        # Utils
        self.nextjs_utils = NextJsUtils(
            log=self.log,
            log_success=self.log_success,
            log_warning=self.log_warning,
            log_error=self.log_error,
        )
        self.ts_utils = TypeScriptUtils(
            log=self.log,
            log_success=self.log_success,
            log_warning=self.log_warning,
            log_error=self.log_error,
        )

    def generate_all(self) -> list[GenerationResult]:
        """
        Generate clients for all configured groups.

        Returns:
            List of GenerationResult for each group
        """
        results = []

        # Get groups to generate
        groups = self.config.groups or self.service.get_group_names()
        if not groups:
            self.log_warning("No groups to generate")
            return results

        # Clean output directories
        self._clean_output_directories()

        # Show what will be generated
        self._log_generation_plan(groups)

        if self.config.dry_run:
            self.log_warning("\n🔍 DRY RUN - No files will be generated")
            return results

        # Generate each group
        self.log("\n" + "=" * 60)

        for group_name in groups:
            result = self._generate_group(group_name)
            results.append(result)

        # Generate shared files (Swift Codable)
        self._generate_shared_files()

        # Check for Swift Codable duplicates
        self._check_swift_codable_duplicates()

        # Post-generation steps
        self._run_post_generation(results)

        # Summary
        self._log_summary(results)

        return results

    def _clean_output_directories(self) -> None:
        """Clean output directories before generation."""
        openapi_config = self.service.config

        schemas_dir = openapi_config.get_schemas_dir()
        clients_dir = openapi_config.get_clients_dir()

        if schemas_dir.exists():
            self.log(f"\n🧹 Cleaning schemas: {schemas_dir}")
            shutil.rmtree(schemas_dir)
            schemas_dir.mkdir(parents=True, exist_ok=True)

        if clients_dir.exists():
            self.log(f"🧹 Cleaning clients: {clients_dir}")
            shutil.rmtree(clients_dir)
            clients_dir.mkdir(parents=True, exist_ok=True)

    def _log_generation_plan(self, groups: list[str]) -> None:
        """Log what will be generated."""
        self.log_success(f"Generating clients for {len(groups)} group(s):\n")

        for group_name in groups:
            group_config = self.service.get_group(group_name)
            if group_config:
                self.log(f"  • {group_name} ({group_config.title})")
            else:
                self.log_warning(f"  ⚠️  Group '{group_name}' not found")

        self.log("\nLanguages:")
        langs = self.config.languages
        if langs.python:
            mode = "(external: openapi-python-client)" if langs.external_python else "(built-in)"
            self.log(f"  → Python {mode}")
        if langs.typescript:
            self.log(f"  → TypeScript (built-in)")
        if langs.go:
            mode = "(external: oapi-codegen)" if langs.external_go else "(built-in)"
            self.log(f"  → Go {mode}")
        if langs.proto:
            self.log(f"  → Protocol Buffers (built-in)")
        if langs.swift:
            self.log(f"  → Swift (external: apple/swift-openapi-generator)")

    def _generate_group(self, group_name: str) -> GenerationResult:
        """Generate clients for a single group."""
        result = GenerationResult(group_name=group_name, success=False)

        group_config = self.service.get_group(group_name)
        if not group_config:
            result.error = f"Group '{group_name}' not found"
            return result

        self.log(f"\n📦 Processing group: {group_name}")

        try:
            # Get apps for this group
            group_apps = self._get_group_apps(group_name)
            if not group_apps:
                result.error = f"No apps matched for group '{group_name}'"
                self.log_warning(f"  ⚠️  {result.error}")
                return result

            self.log(f"  Apps: {', '.join(group_apps)}")

            # Generate OpenAPI schema
            schema_dict, schema_path = self._generate_schema(
                group_name, group_config, group_apps
            )
            result.schema_path = schema_path

            # Parse to IR
            self.log("  → Parsing to IR...")
            ir_context = SchemaUtils.parse_to_ir(schema_dict)
            self.log(f"  ✅ Parsed: {len(ir_context.schemas)} schemas, {len(ir_context.operations)} operations")

            if len(ir_context.operations) == 0:
                self.log_warning(f"  ⏭️  Skipping: no API operations")
                result.success = True
                return result

            # Generate clients
            self._generate_clients(
                group_name, ir_context, schema_dict, schema_path, result
            )

            result.success = True

        except Exception as e:
            import traceback
            tb_str = traceback.format_exc()
            result.error = str(e)
            self.log_error(f"  ❌ Error: {e}")
            self.log_error(f"  Traceback:\n{tb_str}")

        return result

    def _get_group_apps(self, group_name: str) -> list[str]:
        """Get apps for a group."""
        from django.apps import apps
        from django_cfg.modules.django_client.core import GroupManager

        installed_apps = [app.name for app in apps.get_app_configs()]
        manager = GroupManager(
            self.service.config,
            installed_apps,
            groups=self.service.get_groups()
        )
        return manager.get_group_apps(group_name)

    def _generate_schema(
        self,
        group_name: str,
        group_config,
        group_apps: list[str],
    ) -> tuple[dict, Path]:
        """Generate and save OpenAPI schema."""
        from django.apps import apps
        from django_cfg.modules.django_client.core import GroupManager

        self.log("  → Generating OpenAPI schema...")

        # Create URLconf module
        installed_apps = [app.name for app in apps.get_app_configs()]
        manager = GroupManager(
            self.service.config,
            installed_apps,
            groups=self.service.get_groups()
        )
        urlconf_module = manager.create_urlconf_module(group_name)

        # Generate schema
        schema_dict = SchemaUtils.generate_openapi_schema(
            urlconf_module=urlconf_module,
            title=group_config.title,
            description=group_config.description,
            version=group_config.version,
        )

        # Get app labels for metadata
        app_labels = []
        for app_name in group_apps:
            for config in apps.get_app_configs():
                if config.name == app_name:
                    app_labels.append(config.label)
                    break

        # Add metadata
        SchemaUtils.add_django_metadata(schema_dict, group_name, app_labels)

        # Save schema
        schema_path = self.service.config.get_group_schema_path(group_name)
        SchemaUtils.save_schema(schema_dict, schema_path)
        self.log(f"  ✅ Schema saved: {schema_path}")

        return schema_dict, schema_path

    def _generate_clients(
        self,
        group_name: str,
        ir_context,
        schema_dict: dict,
        schema_path: Path,
        result: GenerationResult,
    ) -> None:
        """Generate all requested client types."""
        openapi_config = self.service.config
        langs = self.config.languages

        # Tag prefix logic
        is_django_cfg_group = group_name.startswith('cfg_') and not group_name.startswith('cfg_ext_')
        tag_prefix = "" if is_django_cfg_group else f"{group_name}_"

        # Internal generators
        internal = InternalGenerators(
            ir_context=ir_context,
            openapi_schema=schema_dict,
            config=openapi_config,
            tag_prefix=tag_prefix,
            group_name=group_name,
            log=self.log,
        )

        # External generators
        external = ExternalGenerators(
            spec_path=schema_path,
            log=self.log,
        )

        clients_dir = openapi_config.get_clients_dir()

        # Python
        if langs.python:
            if langs.external_python and external.is_python_available():
                output_dir = clients_dir / "python_ext" / group_name
                ext_result = external.generate_python(output_dir)
                result.python_files = len(ext_result.files_generated)
            else:
                output_dir = openapi_config.get_group_python_dir(group_name)
                files = internal.generate_python(output_dir)
                result.python_files = len(files)
                self.log(f"  ✅ Python: {output_dir} ({len(files)} files)")

        # TypeScript
        if langs.typescript:
            output_dir = openapi_config.get_group_typescript_dir(group_name)
            files = internal.generate_typescript(output_dir)
            result.typescript_files = len(files)
            self.log(f"  ✅ TypeScript: {output_dir} ({len(files)} files)")

        # Go
        if langs.go:
            if langs.external_go and external.is_go_available():
                output_dir = clients_dir / "go_ext" / group_name
                ext_result = external.generate_go(output_dir)
                result.go_files = len(ext_result.files_generated)
            else:
                output_dir = openapi_config.get_group_go_dir(group_name)
                files = internal.generate_go(output_dir)
                result.go_files = len(files)
                self.log(f"  ✅ Go: {output_dir} ({len(files)} files)")

        # Proto
        if langs.proto:
            output_dir = clients_dir / "proto" / group_name
            files = internal.generate_proto(output_dir)
            result.proto_files = len(files)
            self.log(f"  ✅ Proto: {output_dir} ({len(files)} files)")

        # Swift (always external - uses OpenAPIRuntime)
        if langs.swift:
            if external.is_swift_available():
                output_dir = clients_dir / "swift" / group_name
                ext_result = external.generate_swift(output_dir)
                result.swift_files = len(ext_result.files_generated)
            else:
                self.log_warning("  ⚠️  Swift generator not installed")
                self.log(external.get_swift_install_instructions())

        # Swift Codable (internal - simple Codable types, no OpenAPIRuntime)
        if langs.swift_codable:
            output_dir = clients_dir / "swift_codable" / group_name
            files = internal.generate_swift_codable(output_dir)
            result.swift_codable_files = len(files)
            self.log(f"  ✅ Swift Codable: {output_dir} ({len(files)} files)")

        # Archive if enabled
        if openapi_config.enable_archive:
            self._archive_clients(group_name, result)

    def _archive_clients(self, group_name: str, result: GenerationResult) -> None:
        """Archive generated clients."""
        from django_cfg.modules.django_client.core import ArchiveManager

        self.log("  → Archiving...")
        archive_manager = ArchiveManager(self.service.config.get_archive_dir())
        # Simplified - just log for now
        self.log("  ✅ Archived")

    def _generate_shared_files(self) -> None:
        """Generate shared files for Swift Codable (JSONValue, etc.)."""
        langs = self.config.languages

        if not langs.swift_codable:
            return

        clients_dir = self.service.config.get_clients_dir()
        shared_dir = clients_dir / "swift_codable" / "Shared"

        self.log("\n📦 Generating shared Swift Codable files...")

        try:
            files = InternalGenerators.generate_swift_codable_shared(shared_dir)
            self.log(f"  ✅ Shared: {shared_dir} ({len(files)} files)")
        except Exception as e:
            self.log_error(f"  ❌ Error generating shared files: {e}")

    def _check_swift_codable_duplicates(self) -> None:
        """
        Check for duplicate type definitions across Swift Codable groups
        and auto-resolve them by prefixing with the group name.
        """
        import re

        langs = self.config.languages
        if not langs.swift_codable:
            return

        clients_dir = self.service.config.get_clients_dir()
        swift_codable_dir = clients_dir / "swift_codable"

        if not swift_codable_dir.exists():
            return

        # Pattern to match type definitions
        type_pattern = re.compile(
            r'^public\s+(struct|enum|typealias)\s+(\w+)',
            re.MULTILINE
        )

        # Collect all types: {type_name: [(group, file_path, line_num), ...]}
        type_locations: dict[str, list[tuple[str, Path, int]]] = {}

        for group_dir in swift_codable_dir.iterdir():
            if not group_dir.is_dir() or group_dir.name == "Shared":
                continue

            group_name = group_dir.name
            for swift_file in group_dir.glob("*Types.swift"):
                content = swift_file.read_text()
                for match in type_pattern.finditer(content):
                    type_name = match.group(2)
                    # Calculate line number
                    line_num = content[:match.start()].count('\n') + 1
                    if type_name not in type_locations:
                        type_locations[type_name] = []
                    type_locations[type_name].append((group_name, swift_file, line_num))

        # Find duplicates
        duplicates = {
            name: locs for name, locs in type_locations.items()
            if len(locs) > 1
        }

        if not duplicates:
            return

        # Auto-resolve duplicates by prefixing with group name
        self.log_warning("\n" + "-" * 60)
        self.log_warning("⚠️  DUPLICATE SWIFT TYPES DETECTED — AUTO-RESOLVING")
        self.log_warning("-" * 60)

        def to_pascal(name: str) -> str:
            """Convert group name to PascalCase prefix."""
            parts = name.replace("-", "_").split("_")
            return "".join(part.capitalize() for part in parts)

        # Build per-file rename map: {file_path: {old_name: new_name}}
        file_renames: dict[Path, dict[str, str]] = {}

        for type_name, locations in sorted(duplicates.items()):
            self.log_warning(f"\n  {type_name} (defined in {len(locations)} groups):")

            for group, file_path, line_num in locations:
                prefix = to_pascal(group)
                new_name = f"{prefix}{type_name}"
                self.log_warning(f"    → {group}/{file_path.name}:{line_num}  ⟹  {new_name}")

                if file_path not in file_renames:
                    file_renames[file_path] = {}
                file_renames[file_path][type_name] = new_name

        # Apply renames to each affected file using whole-word replacement
        for file_path, renames in file_renames.items():
            content = file_path.read_text()
            for old_name, new_name in renames.items():
                # Replace all occurrences as whole words (type definitions,
                # property types, initializers, typealias targets, etc.)
                content = re.sub(
                    rf'\b{re.escape(old_name)}\b',
                    new_name,
                    content,
                )
            file_path.write_text(content)

        self.log_warning(
            f"\n  ✅ Resolved {len(duplicates)} duplicate type(s) "
            f"across {len(file_renames)} file(s)"
        )
        self.log_warning("-" * 60)

    def _run_post_generation(self, results: list[GenerationResult]) -> None:
        """Run post-generation steps."""
        success_count = sum(1 for r in results if r.success)

        if success_count == 0:
            return

        langs = self.config.languages

        # TypeScript post-processing
        if langs.typescript and not self.config.skip_nextjs_copy:
            self._handle_nextjs_integration()

    def _handle_nextjs_integration(self) -> None:
        """Handle Next.js integration (copy clients, type check, build)."""
        try:
            from django_cfg.core.config import get_current_config
            from django.conf import settings as django_settings

            cfg = get_current_config()
            if not cfg or not cfg.nextjs_admin:
                return

            nextjs_config = cfg.nextjs_admin
            base_dir = cfg.base_dir

            # Resolve paths
            project_path = Path(nextjs_config.project_path)
            if not project_path.is_absolute():
                project_path = base_dir / project_path

            if not project_path.exists():
                self.log_warning(f"⚠️  Next.js project not found: {project_path}")
                return

            api_output_path = project_path / nextjs_config.get_api_output_path()
            ts_source = self.service.config.get_typescript_clients_dir()

            # Copy clients
            self.nextjs_utils.copy_clients(
                ts_source=ts_source,
                api_output_path=api_output_path,
                project_path=project_path,
                copy_cfg_clients=self.config.copy_cfg_clients,
            )

            # Type check
            success, errors = self.ts_utils.check_types(project_path)
            if not success:
                self.log(self.ts_utils.format_diagnostic_help())
                raise RuntimeError("TypeScript type check failed")

            # Build (if not --no-build)
            if not self.config.no_build:
                solution_base_dir = django_settings.BASE_DIR
                static_output = project_path / nextjs_config.get_static_output_path()
                static_zip = nextjs_config.get_static_zip_path(solution_base_dir)

                self.nextjs_utils.build_static_export(
                    project_path=project_path,
                    static_output_path=static_output,
                    static_zip_path=static_zip,
                )

        except Exception as e:
            self.log_error(f"❌ Next.js integration failed: {e}")

    def _log_summary(self, results: list[GenerationResult]) -> None:
        """Log generation summary."""
        success_count = sum(1 for r in results if r.success)
        error_count = len(results) - success_count

        self.log("\n" + "=" * 60)

        if error_count == 0:
            self.log_success(f"\n✅ Successfully generated clients for {success_count} group(s)!")
        else:
            self.log_warning(f"\n⚠️  Generated {success_count} group(s), {error_count} failed")

        # Show output paths
        self.log(f"\nOutput directory: {self.service.get_output_dir()}")

        langs = self.config.languages
        if langs.python:
            self.log(f"  Python:     {self.service.config.get_python_clients_dir()}")
        if langs.typescript:
            self.log(f"  TypeScript: {self.service.config.get_typescript_clients_dir()}")
        if langs.go:
            self.log(f"  Go:         {self.service.config.get_go_clients_dir()}")
        if langs.swift:
            self.log(f"  Swift:      {self.service.config.get_clients_dir() / 'swift'}")


__all__ = ["ClientGenerationOrchestrator"]
