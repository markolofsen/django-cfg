"""
django_grpc.codegen.compiler — Proto compiler utility.

Compiles .proto files to Python using grpc_tools.protoc.
Moved from archive management/proto/compiler.py → codegen/compiler.py.
"""

from __future__ import annotations

import logging
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class ProtoCompiler:
    """Compiles .proto files to Python using grpc_tools.protoc."""

    def __init__(
        self,
        output_dir: Optional[Path] = None,
        proto_import_path: Optional[Path] = None,
        fix_imports: bool = True,
        verbose: bool = True,
    ):
        self.output_dir = output_dir
        self.proto_import_path = proto_import_path
        self.fix_imports = fix_imports
        self.verbose = verbose

    def compile_file(self, proto_file: Path) -> bool:
        """Compile a single .proto file. Returns True on success."""
        if self.verbose:
            logger.info("Compiling: %s", proto_file)

        output_dir = self.output_dir or proto_file.parent
        proto_import_path = self.proto_import_path or proto_file.parent
        output_dir.mkdir(parents=True, exist_ok=True)

        cmd = [
            sys.executable, "-m", "grpc_tools.protoc",
            f"-I{proto_import_path}",
            f"--python_out={output_dir}",
            f"--grpc_python_out={output_dir}",
            str(proto_file),
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            if result.stdout and self.verbose:
                logger.info("  %s", result.stdout.strip())
            if self.verbose:
                logger.info("  Compiled successfully")
            if self.fix_imports:
                self._fix_imports(proto_file, output_dir)
            return True
        except subprocess.CalledProcessError as e:
            logger.error("  Compilation failed: %s", e.stderr)
            return False

    def compile_directory(self, proto_path: Path, recursive: bool = False) -> tuple[int, int]:
        """Compile all .proto files in a directory. Returns (success, failure) counts."""
        proto_files = self._collect_proto_files(proto_path, recursive)
        if not proto_files:
            logger.warning("No .proto files found in: %s", proto_path)
            return 0, 0

        success_count = 0
        failure_count = 0
        for proto_file in proto_files:
            if self.compile_file(proto_file):
                success_count += 1
            else:
                failure_count += 1
        return success_count, failure_count

    def _collect_proto_files(self, path: Path, recursive: bool) -> list[Path]:
        if path.is_file():
            if path.suffix == ".proto":
                return [path]
            raise ValueError(f"Not a .proto file: {path}")
        return list(path.rglob("*.proto") if recursive else path.glob("*.proto"))

    def _fix_imports(self, proto_file: Path, output_dir: Path) -> None:
        """
        Fix imports in generated _grpc.py files.

        Changes: `import foo_pb2 as foo__pb2`
        To:      `from . import foo_pb2 as foo__pb2`
        """
        grpc_file = output_dir / f"{proto_file.stem}_pb2_grpc.py"
        if not grpc_file.exists():
            return

        content = grpc_file.read_text()
        pattern = r"^import (\w+_pb2) as (\w+)$"

        def replace_func(match):
            module = match.group(1)
            alias = match.group(2)
            return f"from . import {module} as {alias}"

        new_content = re.sub(pattern, replace_func, content, flags=re.MULTILINE)
        if new_content != content:
            grpc_file.write_text(new_content)
            if self.verbose:
                logger.info("  Fixed imports in %s", grpc_file.name)


__all__ = ["ProtoCompiler"]
