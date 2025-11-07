"""
Management command to generate .proto files from Django models.

Usage:
    python manage.py generate_protos [app_label ...]
    python manage.py generate_protos crypto
    python manage.py generate_protos crypto accounts
    python manage.py generate_protos --all
"""

from django.core.management.base import CommandError
from django.apps import apps

from django_cfg.management.utils import AdminCommand


class Command(AdminCommand):
    command_name = 'generate_protos'
    help = "Generate .proto files from Django models"

    def add_arguments(self, parser):
        parser.add_argument(
            "apps",
            nargs="*",
            type=str,
            help="App labels to generate protos for",
        )
        parser.add_argument(
            "--all",
            action="store_true",
            help="Generate protos for all enabled apps from GRPC config",
        )
        parser.add_argument(
            "--output-dir",
            type=str,
            default=None,
            help="Custom output directory (overrides config)",
        )
        parser.add_argument(
            "--compile",
            action="store_true",
            help="Automatically compile generated .proto files to Python",
        )
        parser.add_argument(
            "--no-fix-imports",
            action="store_false",
            dest="fix_imports",
            help="Disable import fixing when compiling (only with --compile)",
        )

    def handle(self, *args, **options):
        from django_cfg.apps.integrations.grpc.utils.proto_gen import generate_proto_for_app
        from django_cfg.apps.integrations.grpc.services.management.config_helper import get_grpc_config

        # Get gRPC config
        grpc_config = get_grpc_config()
        if not grpc_config or not grpc_config.enabled:
            raise CommandError("gRPC is not enabled in configuration")

        # Determine which apps to generate
        app_labels = options["apps"]

        if options["all"]:
            # Use enabled_apps from config
            app_labels = grpc_config.enabled_apps
            if not app_labels:
                raise CommandError("No enabled_apps configured in GRPCConfig")
            self.stdout.write(
                self.style.SUCCESS(
                    f"Generating protos for all enabled apps: {', '.join(app_labels)}"
                )
            )
        elif not app_labels:
            # No apps specified - show help
            raise CommandError(
                "Please specify app labels or use --all flag\n"
                "Examples:\n"
                "  python manage.py generate_protos crypto\n"
                "  python manage.py generate_protos crypto accounts\n"
                "  python manage.py generate_protos --all"
            )

        # Validate apps exist
        for app_label in app_labels:
            try:
                apps.get_app_config(app_label)
            except LookupError:
                raise CommandError(f"App '{app_label}' not found")

        # Get output directory from options or config
        output_dir = None
        if options["output_dir"]:
            from pathlib import Path
            output_dir = Path(options["output_dir"])
            self.stdout.write(
                self.style.WARNING(f"Using custom output directory: {output_dir}")
            )

        # Generate protos
        total_generated = 0
        for app_label in app_labels:
            self.stdout.write(f"\n📦 Generating proto for app: {app_label}")

            try:
                count = generate_proto_for_app(app_label, output_dir=output_dir)
                if count > 0:
                    total_generated += count
                    self.stdout.write(
                        self.style.SUCCESS(f"   ✅ Generated {app_label}.proto")
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f"   ⚠️  No models found in {app_label}")
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"   ❌ Failed: {e}")
                )

        # Summary
        self.stdout.write("\n" + "=" * 70)
        if total_generated > 0:
            # Show output location
            if output_dir:
                output_location = output_dir
            elif grpc_config.proto and grpc_config.proto.output_dir:
                output_location = grpc_config.proto.output_dir
            else:
                output_location = "media/protos"

            self.stdout.write(
                self.style.SUCCESS(
                    f"🎉 Generated {total_generated} proto file(s)\n"
                    f"📂 Output directory: {output_location}"
                )
            )

            # Compile proto files if requested
            if options["compile"]:
                self.stdout.write("\n" + "=" * 70)
                self.stdout.write(self.style.SUCCESS("🔧 Compiling generated proto files..."))
                self._compile_protos(output_location, options.get("fix_imports", True))
        else:
            self.stdout.write(
                self.style.WARNING("⚠️  No proto files generated")
            )
        self.stdout.write("=" * 70)

    def _compile_protos(self, output_dir, fix_imports: bool):
        """Compile all .proto files in output directory."""
        from pathlib import Path
        from django_cfg.apps.integrations.grpc.management.proto.compiler import ProtoCompiler

        output_path = Path(output_dir)
        if not output_path.exists():
            self.stdout.write(self.style.ERROR(f"   ❌ Output directory not found: {output_dir}"))
            return

        # Create compiler
        compiler = ProtoCompiler(
            output_dir=output_path / "generated",  # Compile to generated/ subdirectory
            proto_import_path=output_path,
            fix_imports=fix_imports,
            verbose=True,
        )

        # Compile all proto files
        success_count, failure_count = compiler.compile_directory(
            output_path,
            recursive=False,
        )

        if failure_count > 0:
            self.stdout.write(
                self.style.ERROR(
                    f"   ❌ Failed to compile {failure_count} proto file(s) "
                    f"({success_count} succeeded)"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"   ✅ Compiled {success_count} proto file(s) successfully"
                )
            )
