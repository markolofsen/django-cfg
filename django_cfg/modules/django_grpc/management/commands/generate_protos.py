"""
Django management command to generate .proto files from Django models.

Usage:
    python manage.py generate_protos crypto
    python manage.py generate_protos crypto accounts
    python manage.py generate_protos --all
    python manage.py generate_protos --all --compile
"""

from __future__ import annotations

import logging
from pathlib import Path

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError

logger = logging.getLogger(__name__)


class Command(BaseCommand):
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
            help="Generate protos for all enabled apps from gRPC config",
        )
        parser.add_argument(
            "--output-dir",
            type=str,
            default=None,
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
        )

    def handle(self, *args, **options):
        from django_cfg.modules.django_grpc.utils.proto_gen import generate_proto_for_app

        app_labels = options["apps"]

        if options["all"]:
            # Try to get enabled apps from grpc_module config
            try:
                from django_cfg.modules.django_grpc.services.management.config_helper import (
                    get_grpc_module_config,
                )
                grpc_cfg = get_grpc_module_config()
                app_labels = list(grpc_cfg.enabled_apps) if grpc_cfg else []
            except Exception:
                app_labels = []
            if not app_labels:
                raise CommandError("No enabled_apps configured in DjangoGrpcModuleConfig")

        if not app_labels:
            raise CommandError(
                "Please specify app labels or use --all flag\n"
                "  python manage.py generate_protos crypto\n"
                "  python manage.py generate_protos --all"
            )

        for app_label in app_labels:
            try:
                apps.get_app_config(app_label)
            except LookupError:
                raise CommandError(f"App '{app_label}' not found")

        output_dir = Path(options["output_dir"]) if options.get("output_dir") else None

        total_generated = 0
        for app_label in app_labels:
            self.stdout.write(f"Generating proto for app: {app_label}")
            try:
                count = generate_proto_for_app(app_label, output_dir=output_dir)
                if count > 0:
                    total_generated += count
                    self.stdout.write(self.style.SUCCESS(f"  Generated {app_label}.proto"))
                else:
                    self.stdout.write(self.style.WARNING(f"  No models found in {app_label}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  Failed: {e}"))

        if total_generated > 0:
            self.stdout.write(self.style.SUCCESS(f"Generated {total_generated} proto file(s)"))
            if options.get("compile") and output_dir:
                self._compile_protos(output_dir, options.get("fix_imports", True))
        else:
            self.stdout.write(self.style.WARNING("No proto files generated"))

    def _compile_protos(self, output_dir: Path, fix_imports: bool) -> None:
        from django_cfg.modules.django_grpc.codegen.compiler import ProtoCompiler

        if not output_dir.exists():
            self.stdout.write(self.style.ERROR(f"Output directory not found: {output_dir}"))
            return

        compiler = ProtoCompiler(
            output_dir=output_dir / "generated",
            proto_import_path=output_dir,
            fix_imports=fix_imports,
            verbose=True,
        )
        success_count, failure_count = compiler.compile_directory(output_dir, recursive=False)
        if failure_count > 0:
            self.stdout.write(self.style.ERROR(
                f"Failed to compile {failure_count} proto file(s) ({success_count} succeeded)"
            ))
        else:
            self.stdout.write(self.style.SUCCESS(f"Compiled {success_count} proto file(s)"))
