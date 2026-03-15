"""
Proto compiler utilities.
Shared functionality for compiling .proto files to Python.
"""

import logging
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

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
        """
        Initialize proto compiler.

        Args:
            output_dir: Output directory for generated files (default: same as proto file)
            proto_import_path: Additional proto import path (passed to protoc -I flag)
            fix_imports: Fix imports in generated _grpc.py files (default: True)
            verbose: Print compilation progress (default: True)
        """
        self.output_dir = output_dir
        self.proto_import_path = proto_import_path
        self.fix_imports = fix_imports
        self.verbose = verbose

    def compile_file(self, proto_file: Path) -> bool:
        """
        Compile a single .proto file.

        Args:
            proto_file: Path to .proto file

        Returns:
            True if compilation succeeded, False otherwise
        """
        if self.verbose:
            logger.info(f"📦 Compiling: {proto_file}")

        # Determine output directory
        output_dir = self.output_dir or proto_file.parent

        # Determine proto import path
        proto_import_path = self.proto_import_path or proto_file.parent

        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        # Build protoc command
        cmd = [
            sys.executable,
            "-m",
            "grpc_tools.protoc",
            f"-I{proto_import_path}",
            f"--python_out={output_dir}",
            f"--grpc_python_out={output_dir}",
            str(proto_file),
        ]

        # Run protoc
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
            )

            if result.stdout and self.verbose:
                logger.info(f"   {result.stdout}")

            if self.verbose:
                logger.info(f"   ✅ Compiled successfully")

            # Fix imports if requested
            if self.fix_imports:
                self._fix_imports(proto_file, output_dir)

            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"   ❌ Compilation failed")
            logger.error(f"   Error: {e.stderr}")
            return False

    def compile_directory(
        self,
        proto_path: Path,
        recursive: bool = False,
    ) -> tuple[int, int]:
        """
        Compile all .proto files in a directory.

        Args:
            proto_path: Directory containing .proto files
            recursive: Recursively compile all .proto files

        Returns:
            Tuple of (success_count, failure_count)
        """
        # Collect proto files
        proto_files = self._collect_proto_files(proto_path, recursive)

        if not proto_files:
            logger.warning(f"No .proto files found in: {proto_path}")
            return 0, 0

        if self.verbose:
            logger.info(f"🔧 Compiling {len(proto_files)} proto file(s)...")

        # Compile each proto file
        success_count = 0
        failure_count = 0

        for proto_file in proto_files:
            if self.compile_file(proto_file):
                success_count += 1
            else:
                failure_count += 1

        return success_count, failure_count

    def _collect_proto_files(self, path: Path, recursive: bool) -> List[Path]:
        """Collect all .proto files from path."""
        if path.is_file():
            if path.suffix == ".proto":
                return [path]
            else:
                raise ValueError(f"File is not a .proto file: {path}")

        # Directory
        if recursive:
            return list(path.rglob("*.proto"))
        else:
            return list(path.glob("*.proto"))

    def _fix_imports(self, proto_file: Path, output_dir: Path):
        """
        Fix imports in generated _grpc.py files.

        Changes: import foo_pb2 as foo__pb2
        To:      from . import foo_pb2 as foo__pb2
        """
        # Find generated _grpc.py file
        grpc_file = output_dir / f"{proto_file.stem}_pb2_grpc.py"

        if not grpc_file.exists():
            if self.verbose:
                logger.warning(f"   ⚠️  Skipping import fix: {grpc_file.name} not found")
            return

        if self.verbose:
            logger.info(f"   🔧 Fixing imports in {grpc_file.name}...")

        # Read file
        content = grpc_file.read_text()

        # Pattern to match: import xxx_pb2 as yyy
        # But NOT: from xxx import ...
        pattern = r"^import (\w+_pb2) as (\w+)$"

        # Replace with: from . import xxx_pb2 as yyy
        def replace_func(match):
            module = match.group(1)
            alias = match.group(2)
            return f"from . import {module} as {alias}"

        # Apply replacement
        new_content = re.sub(pattern, replace_func, content, flags=re.MULTILINE)

        # Count changes
        changes = content.count("\nimport ") - new_content.count("\nimport ")

        if changes > 0:
            # Write back
            grpc_file.write_text(new_content)
            if self.verbose:
                logger.info(f"   ✅ Fixed {changes} import(s) in {grpc_file.name}")
        else:
            if self.verbose:
                logger.info(f"   ℹ️  No imports to fix in {grpc_file.name}")
