"""
Betterproto2 compilation utilities.

Compiles .proto files to Python using betterproto2 with Pydantic dataclasses.

Features:
- Modern async stubs using grpclib
- Pydantic dataclass messages with validation
- Optional JSON serialization support
- Compatible with django-cfg resilience patterns

Usage:
    from django_cfg.apps.integrations.grpc.utils.betterproto_compiler import (
        compile_proto,
        compile_protos_directory,
        BetterprotoCompiler,
    )

    # Compile single file
    compile_proto("protos/service.proto", "generated/")

    # Compile directory
    compile_protos_directory("protos/", "generated/")

    # With options
    compiler = BetterprotoCompiler(pydantic_dataclasses=True)
    compiler.compile("protos/", "generated/")

Created: 2025-12-31
"""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Sequence

logger = logging.getLogger(__name__)


# =============================================================================
# Check for betterproto2 compiler
# =============================================================================


def is_betterproto2_available() -> bool:
    """Check if betterproto2 compiler is available."""
    try:
        from betterproto2 import Message
        return True
    except ImportError:
        return False


def is_protoc_available() -> bool:
    """Check if protoc is available in PATH."""
    return shutil.which("protoc") is not None


def get_protoc_version() -> Optional[str]:
    """Get protoc version."""
    if not is_protoc_available():
        return None
    try:
        result = subprocess.run(
            ["protoc", "--version"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None


# =============================================================================
# Compiler Configuration
# =============================================================================


@dataclass
class BetterprotoCompilerConfig:
    """Configuration for betterproto2 compilation."""

    # Output settings
    pydantic_dataclasses: bool = True
    """Generate Pydantic dataclasses for validation."""

    include_google_types: bool = True
    """Include google well-known types."""

    generate_init: bool = True
    """Generate __init__.py in output directories."""

    # Path settings
    proto_paths: List[Path] = field(default_factory=list)
    """Additional proto include paths."""

    # Code generation
    typing_imports: bool = True
    """Add typing imports to generated code."""

    service_suffix: str = "Stub"
    """Suffix for generated service classes."""


# =============================================================================
# Betterproto2 Compiler
# =============================================================================


class BetterprotoCompiler:
    """
    Compiles .proto files to Python using betterproto2.

    Generates modern async gRPC code with:
    - Pydantic dataclass messages
    - grpclib async stubs
    - Type hints

    Usage:
        compiler = BetterprotoCompiler()

        # Compile single file
        compiler.compile_file("service.proto", "generated/")

        # Compile directory
        compiler.compile_directory("protos/", "generated/")
    """

    def __init__(self, config: Optional[BetterprotoCompilerConfig] = None):
        """
        Initialize compiler.

        Args:
            config: Compiler configuration
        """
        self.config = config or BetterprotoCompilerConfig()

    def compile_file(
        self,
        proto_file: Path | str,
        output_dir: Path | str,
        proto_path: Optional[Path | str] = None,
    ) -> bool:
        """
        Compile single .proto file.

        Args:
            proto_file: Path to .proto file
            output_dir: Output directory for generated code
            proto_path: Proto include path (default: parent of proto_file)

        Returns:
            True if compilation succeeded
        """
        proto_file = Path(proto_file)
        output_dir = Path(output_dir)

        if not proto_file.exists():
            logger.error(f"Proto file not found: {proto_file}")
            return False

        if proto_path is None:
            proto_path = proto_file.parent

        proto_path = Path(proto_path)

        # Build command
        cmd = self._build_command(
            proto_files=[proto_file],
            output_dir=output_dir,
            proto_paths=[proto_path] + self.config.proto_paths,
        )

        return self._run_command(cmd)

    def compile_directory(
        self,
        proto_dir: Path | str,
        output_dir: Path | str,
        recursive: bool = True,
    ) -> bool:
        """
        Compile all .proto files in directory.

        Args:
            proto_dir: Directory containing .proto files
            output_dir: Output directory for generated code
            recursive: Recursively compile subdirectories

        Returns:
            True if all compilations succeeded
        """
        proto_dir = Path(proto_dir)
        output_dir = Path(output_dir)

        if not proto_dir.exists():
            logger.error(f"Proto directory not found: {proto_dir}")
            return False

        # Find all proto files
        pattern = "**/*.proto" if recursive else "*.proto"
        proto_files = list(proto_dir.glob(pattern))

        if not proto_files:
            logger.warning(f"No .proto files found in {proto_dir}")
            return True

        logger.info(f"Found {len(proto_files)} proto file(s) in {proto_dir}")

        # Build command
        cmd = self._build_command(
            proto_files=proto_files,
            output_dir=output_dir,
            proto_paths=[proto_dir] + self.config.proto_paths,
        )

        success = self._run_command(cmd)

        if success and self.config.generate_init:
            self._generate_init_files(output_dir)

        return success

    def _build_command(
        self,
        proto_files: Sequence[Path],
        output_dir: Path,
        proto_paths: Sequence[Path],
    ) -> List[str]:
        """Build protoc command with betterproto2 plugin."""
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        cmd = ["python", "-m", "grpc_tools.protoc"]

        # Add proto paths
        for path in proto_paths:
            cmd.extend(["-I", str(path)])

        # Add google proto path if requested
        if self.config.include_google_types:
            google_proto = self._find_google_proto_path()
            if google_proto:
                cmd.extend(["-I", str(google_proto)])

        # Add betterproto2 output
        betterproto_out = f"--python_betterproto2_out={output_dir}"
        cmd.append(betterproto_out)

        # Add pydantic option if enabled
        if self.config.pydantic_dataclasses:
            # Note: betterproto2 uses pydantic by default
            pass

        # Add proto files
        cmd.extend(str(f) for f in proto_files)

        return cmd

    def _run_command(self, cmd: List[str]) -> bool:
        """Execute compilation command."""
        logger.debug(f"Running: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode != 0:
                logger.error(f"Compilation failed: {result.stderr}")
                return False

            if result.stderr:
                logger.warning(f"Compiler warnings: {result.stderr}")

            logger.info("Betterproto2 compilation successful")
            return True

        except FileNotFoundError as e:
            logger.error(f"Command not found: {e}")
            return False
        except Exception as e:
            logger.error(f"Compilation error: {e}")
            return False

    def _find_google_proto_path(self) -> Optional[Path]:
        """Find google protobuf include path."""
        try:
            import grpc_tools
            grpc_tools_path = Path(grpc_tools.__file__).parent
            proto_path = grpc_tools_path / "_proto"
            if proto_path.exists():
                return proto_path
        except ImportError:
            pass

        # Try site-packages
        for site_dir in sys.path:
            proto_path = Path(site_dir) / "grpc_tools" / "_proto"
            if proto_path.exists():
                return proto_path

        return None

    def _generate_init_files(self, output_dir: Path) -> None:
        """Generate __init__.py files in output directories."""
        for dirpath, dirnames, filenames in os.walk(output_dir):
            dirpath = Path(dirpath)

            # Skip if no .py files
            py_files = [f for f in filenames if f.endswith(".py") and f != "__init__.py"]
            if not py_files:
                continue

            init_file = dirpath / "__init__.py"
            if not init_file.exists():
                # Create minimal init
                imports = []
                for f in py_files:
                    module = f[:-3]  # Remove .py
                    imports.append(f"from .{module} import *")

                init_content = '"""Auto-generated by betterproto2 compiler."""\n\n'
                init_content += "\n".join(imports) + "\n"

                init_file.write_text(init_content)
                logger.debug(f"Generated {init_file}")


# =============================================================================
# Alternative: Direct betterproto2 compilation
# =============================================================================


class Betterproto2DirectCompiler:
    """
    Direct betterproto2 compilation using Python API.

    This compiler uses betterproto2's Python API directly instead of
    the protoc plugin, which can be more reliable in some environments.

    Usage:
        compiler = Betterproto2DirectCompiler()
        compiler.compile("protos/", "generated/")
    """

    def __init__(self, config: Optional[BetterprotoCompilerConfig] = None):
        """Initialize compiler."""
        self.config = config or BetterprotoCompilerConfig()

    def compile(
        self,
        proto_source: Path | str,
        output_dir: Path | str,
    ) -> bool:
        """
        Compile protos using betterproto2_compiler.

        Args:
            proto_source: Proto file or directory
            output_dir: Output directory

        Returns:
            True if successful
        """
        proto_source = Path(proto_source)
        output_dir = Path(output_dir)

        try:
            # Try using betterproto2_compiler CLI
            cmd = [
                sys.executable,
                "-m",
                "betterproto2_compiler",
                "--output", str(output_dir),
            ]

            # Add proto path
            if proto_source.is_dir():
                cmd.extend(["--proto-path", str(proto_source)])
                proto_files = list(proto_source.glob("**/*.proto"))
                cmd.extend(str(f) for f in proto_files)
            else:
                cmd.extend(["--proto-path", str(proto_source.parent)])
                cmd.append(str(proto_source))

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode != 0:
                logger.error(f"betterproto2_compiler failed: {result.stderr}")

                # Try alternative with buf
                return self._compile_with_buf(proto_source, output_dir)

            logger.info("Betterproto2 direct compilation successful")
            return True

        except FileNotFoundError:
            logger.warning("betterproto2_compiler not found, trying buf")
            return self._compile_with_buf(proto_source, output_dir)

    def _compile_with_buf(
        self,
        proto_source: Path,
        output_dir: Path,
    ) -> bool:
        """Compile using buf (if available)."""
        if not shutil.which("buf"):
            logger.error("Neither betterproto2_compiler nor buf found")
            return False

        # Create buf.gen.yaml
        buf_config = proto_source.parent / "buf.gen.yaml" if proto_source.is_file() else proto_source / "buf.gen.yaml"

        config_content = f"""version: v2
plugins:
  - remote: buf.build/community/danielgtaylor-python-betterproto
    out: {output_dir}
"""

        buf_config.write_text(config_content)

        try:
            cmd = ["buf", "generate"]
            if proto_source.is_file():
                cmd.append(str(proto_source.parent))
            else:
                cmd.append(str(proto_source))

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
                cwd=str(proto_source.parent) if proto_source.is_file() else str(proto_source),
            )

            if result.returncode != 0:
                logger.error(f"buf generate failed: {result.stderr}")
                return False

            logger.info("Buf compilation successful")
            return True

        finally:
            # Cleanup temp config
            if buf_config.exists():
                buf_config.unlink()


# =============================================================================
# Convenience Functions
# =============================================================================


def compile_proto(
    proto_file: Path | str,
    output_dir: Path | str,
    pydantic: bool = True,
) -> bool:
    """
    Compile single .proto file to betterproto2 Python code.

    Args:
        proto_file: Path to .proto file
        output_dir: Output directory
        pydantic: Enable Pydantic dataclasses

    Returns:
        True if compilation succeeded

    Example:
        >>> compile_proto("service.proto", "generated/")
        True
    """
    config = BetterprotoCompilerConfig(pydantic_dataclasses=pydantic)
    compiler = BetterprotoCompiler(config)
    return compiler.compile_file(proto_file, output_dir)


def compile_protos_directory(
    proto_dir: Path | str,
    output_dir: Path | str,
    recursive: bool = True,
    pydantic: bool = True,
) -> bool:
    """
    Compile all .proto files in directory to betterproto2 Python code.

    Args:
        proto_dir: Directory containing .proto files
        output_dir: Output directory
        recursive: Recursively compile subdirectories
        pydantic: Enable Pydantic dataclasses

    Returns:
        True if all compilations succeeded

    Example:
        >>> compile_protos_directory("protos/", "generated/")
        True
    """
    config = BetterprotoCompilerConfig(pydantic_dataclasses=pydantic)
    compiler = BetterprotoCompiler(config)
    return compiler.compile_directory(proto_dir, output_dir, recursive=recursive)


def compile_betterproto2(
    source: Path | str,
    output_dir: Path | str,
) -> bool:
    """
    Smart compile using best available method.

    Tries in order:
    1. betterproto2_compiler (if available)
    2. protoc with betterproto2 plugin
    3. buf with betterproto plugin

    Args:
        source: Proto file or directory
        output_dir: Output directory

    Returns:
        True if compilation succeeded
    """
    source = Path(source)
    output_dir = Path(output_dir)

    # Try direct compiler first
    direct = Betterproto2DirectCompiler()
    if direct.compile(source, output_dir):
        return True

    # Fall back to protoc plugin
    compiler = BetterprotoCompiler()
    if source.is_dir():
        return compiler.compile_directory(source, output_dir)
    else:
        return compiler.compile_file(source, output_dir)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Check functions
    "is_betterproto2_available",
    "is_protoc_available",
    "get_protoc_version",
    # Config
    "BetterprotoCompilerConfig",
    # Compilers
    "BetterprotoCompiler",
    "Betterproto2DirectCompiler",
    # Convenience functions
    "compile_proto",
    "compile_protos_directory",
    "compile_betterproto2",
]
