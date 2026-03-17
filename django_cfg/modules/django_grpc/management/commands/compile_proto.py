"""
Django management command to compile .proto files to Python.

Usage:
    python manage.py compile_proto path/to/file.proto
    python manage.py compile_proto path/to/file.proto --output-dir generated/
    python manage.py compile_proto path/to/protos/ --recursive
"""

from __future__ import annotations

import logging
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Compile .proto files to Python using grpc_tools.protoc"

    def add_arguments(self, parser):
        parser.add_argument(
            "proto_path",
            type=str,
            help="Path to .proto file or directory containing .proto files",
        )
        parser.add_argument(
            "--output-dir",
            type=str,
            default=None,
            help="Output directory for generated files (default: same as proto file)",
        )
        parser.add_argument(
            "--proto-path",
            type=str,
            default=None,
            help="Additional proto import path (-I flag passed to protoc)",
        )
        parser.add_argument(
            "--fix-imports",
            action="store_true",
            default=True,
            help="Fix imports in generated _grpc.py files (default: True)",
        )
        parser.add_argument(
            "--no-fix-imports",
            action="store_false",
            dest="fix_imports",
        )
        parser.add_argument(
            "--recursive",
            action="store_true",
            help="Recursively compile all .proto files in directory",
        )

    def handle(self, *args, **options):
        from django_cfg.modules.django_grpc.codegen.compiler import ProtoCompiler

        proto_path = Path(options["proto_path"])
        output_dir = Path(options["output_dir"]) if options["output_dir"] else None
        proto_import_path = Path(options["proto_path"]) if options.get("proto_path") else None

        if not proto_path.exists():
            raise CommandError(f"Path does not exist: {proto_path}")

        compiler = ProtoCompiler(
            output_dir=output_dir,
            proto_import_path=proto_import_path,
            fix_imports=options["fix_imports"],
            verbose=True,
        )

        if proto_path.is_file():
            success = compiler.compile_file(proto_path)
            if not success:
                raise CommandError(f"Failed to compile {proto_path}")
        else:
            success_count, failure_count = compiler.compile_directory(
                proto_path,
                recursive=options["recursive"],
            )
            if failure_count > 0:
                raise CommandError(
                    f"Failed to compile {failure_count} proto file(s) "
                    f"({success_count} succeeded)"
                )

        self.stdout.write(self.style.SUCCESS("Done! All proto files compiled successfully."))
