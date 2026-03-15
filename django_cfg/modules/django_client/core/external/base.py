"""
External Code Generators - Base Classes.

This module provides the foundation for integrating external CLI-based
code generators (like apple/swift-openapi-generator, oapi-codegen, etc.)
into our Django workflow.
"""

from __future__ import annotations

import shutil
import subprocess
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class GeneratorLanguage(str, Enum):
    """Supported languages for external generators."""
    SWIFT = "swift"
    GO = "go"
    PYTHON = "python"


@dataclass
class GenerationResult:
    """Result of a code generation operation."""
    success: bool
    language: GeneratorLanguage
    output_dir: Path
    files_generated: list[str] = field(default_factory=list)
    error: str | None = None
    warnings: list[str] = field(default_factory=list)
    stdout: str = ""
    stderr: str = ""
    duration_ms: int = 0

    def __str__(self) -> str:
        if self.success:
            return f"Generated {len(self.files_generated)} {self.language.value} files"
        return f"Generation failed: {self.error}"


@dataclass
class GeneratorConfig:
    """Configuration for external generators."""
    # Common options
    package_name: str | None = None
    output_subdir: str | None = None

    # Swift-specific
    swift_access_modifier: str = "public"
    swift_generate_types: bool = True
    swift_generate_client: bool = True

    # Go-specific
    go_package: str | None = None
    go_generate_client: bool = True
    go_generate_models: bool = True
    go_server_framework: str | None = None  # chi, echo, fiber, gin, net-http

    # Python-specific
    python_project_name: str | None = None
    python_package_name: str | None = None
    python_use_async: bool = True

    # Extra options passed directly to CLI
    extra_args: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            k: v for k, v in self.__dict__.items()
            if v is not None and v != [] and v != ""
        }


class ExternalGeneratorError(Exception):
    """Base exception for external generator errors."""
    pass


class GeneratorNotInstalledError(ExternalGeneratorError):
    """Raised when the CLI tool is not installed."""
    def __init__(self, generator_name: str, install_instructions: str):
        self.generator_name = generator_name
        self.install_instructions = install_instructions
        super().__init__(
            f"{generator_name} is not installed.\n"
            f"Installation instructions:\n{install_instructions}"
        )


class GeneratorExecutionError(ExternalGeneratorError):
    """Raised when the CLI tool fails to execute."""
    def __init__(self, generator_name: str, stderr: str, returncode: int):
        self.generator_name = generator_name
        self.stderr = stderr
        self.returncode = returncode
        super().__init__(
            f"{generator_name} failed with exit code {returncode}:\n{stderr}"
        )


class ExternalGenerator(ABC):
    """
    Abstract base class for external CLI-based code generators.

    Subclasses must implement:
    - language: The target language
    - cli_command: The CLI command to invoke
    - check_installation: Verify the CLI is available
    - install_instructions: How to install the CLI
    - _build_command: Build the CLI command with arguments

    Usage:
        generator = SwiftOpenAPIGenerator()
        if not generator.check_installation():
            print(generator.install_instructions())
            return

        result = generator.generate(
            spec_path=Path("openapi.yaml"),
            output_dir=Path("generated/"),
            config=GeneratorConfig(package_name="MyAPI")
        )

        if result.success:
            print(f"Generated {len(result.files_generated)} files")
    """

    @property
    @abstractmethod
    def language(self) -> GeneratorLanguage:
        """Target language for this generator."""
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name for logging."""
        ...

    @property
    @abstractmethod
    def cli_command(self) -> str:
        """Primary CLI command to invoke."""
        ...

    @property
    def version_command(self) -> list[str]:
        """Command to check version. Override if different from --version."""
        return [self.cli_command, "--version"]

    @abstractmethod
    def install_instructions(self) -> str:
        """Return installation instructions for this generator."""
        ...

    @abstractmethod
    def _build_command(
        self,
        spec_path: Path,
        output_dir: Path,
        config: GeneratorConfig | None = None,
    ) -> list[str]:
        """
        Build the CLI command with all arguments.

        Args:
            spec_path: Path to the OpenAPI spec file
            output_dir: Directory for generated output
            config: Optional configuration

        Returns:
            List of command arguments
        """
        ...

    def check_installation(self) -> bool:
        """
        Check if the CLI tool is installed and accessible.

        Returns:
            True if installed, False otherwise
        """
        if shutil.which(self.cli_command) is None:
            return False

        try:
            result = subprocess.run(
                self.version_command,
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return False

    def get_version(self) -> str | None:
        """
        Get the installed version of the CLI tool.

        Returns:
            Version string or None if not available
        """
        try:
            result = subprocess.run(
                self.version_command,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                # Usually version is in stdout, sometimes stderr
                output = result.stdout.strip() or result.stderr.strip()
                # Extract version from output (handle various formats)
                return output.split('\n')[0]
            return None
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return None

    def generate(
        self,
        spec_path: Path,
        output_dir: Path,
        config: GeneratorConfig | None = None,
        *,
        timeout: int = 300,
        check_installation: bool = True,
    ) -> GenerationResult:
        """
        Generate client code from an OpenAPI specification.

        Args:
            spec_path: Path to the OpenAPI spec file (YAML or JSON)
            output_dir: Directory for generated output
            config: Optional configuration options
            timeout: Maximum execution time in seconds
            check_installation: Whether to verify CLI is installed first

        Returns:
            GenerationResult with success status and details

        Raises:
            GeneratorNotInstalledError: If CLI is not installed and check_installation=True
            FileNotFoundError: If spec_path doesn't exist
        """
        import time
        start_time = time.monotonic()

        # Validate inputs
        spec_path = Path(spec_path).resolve()
        output_dir = Path(output_dir).resolve()

        if not spec_path.exists():
            return GenerationResult(
                success=False,
                language=self.language,
                output_dir=output_dir,
                error=f"OpenAPI spec not found: {spec_path}",
            )

        # Check installation
        if check_installation and not self.check_installation():
            raise GeneratorNotInstalledError(
                self.name,
                self.install_instructions()
            )

        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        # Build command
        command = self._build_command(spec_path, output_dir, config)

        logger.info(f"Running {self.name}: {' '.join(command)}")

        # Execute
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=output_dir,
            )

            duration_ms = int((time.monotonic() - start_time) * 1000)

            if result.returncode != 0:
                return GenerationResult(
                    success=False,
                    language=self.language,
                    output_dir=output_dir,
                    error=f"Exit code {result.returncode}",
                    stdout=result.stdout,
                    stderr=result.stderr,
                    duration_ms=duration_ms,
                )

            # Collect generated files
            files = self._collect_generated_files(output_dir)
            warnings = self._parse_warnings(result.stderr)

            return GenerationResult(
                success=True,
                language=self.language,
                output_dir=output_dir,
                files_generated=files,
                warnings=warnings,
                stdout=result.stdout,
                stderr=result.stderr,
                duration_ms=duration_ms,
            )

        except subprocess.TimeoutExpired:
            duration_ms = int((time.monotonic() - start_time) * 1000)
            return GenerationResult(
                success=False,
                language=self.language,
                output_dir=output_dir,
                error=f"Timeout after {timeout}s",
                duration_ms=duration_ms,
            )
        except OSError as e:
            duration_ms = int((time.monotonic() - start_time) * 1000)
            return GenerationResult(
                success=False,
                language=self.language,
                output_dir=output_dir,
                error=str(e),
                duration_ms=duration_ms,
            )

    def _collect_generated_files(self, output_dir: Path) -> list[str]:
        """
        Collect list of generated files.

        Override in subclasses for custom file patterns.
        """
        extensions = self._get_file_extensions()
        files = []

        for ext in extensions:
            for file_path in output_dir.rglob(f"*{ext}"):
                files.append(str(file_path.relative_to(output_dir)))

        return sorted(files)

    def _get_file_extensions(self) -> list[str]:
        """Get file extensions for the target language."""
        extensions_map = {
            GeneratorLanguage.SWIFT: [".swift"],
            GeneratorLanguage.GO: [".go"],
            GeneratorLanguage.PYTHON: [".py"],
        }
        return extensions_map.get(self.language, [])

    def _parse_warnings(self, stderr: str) -> list[str]:
        """
        Parse warnings from stderr output.

        Override in subclasses for custom warning patterns.
        """
        warnings = []
        for line in stderr.split('\n'):
            line = line.strip()
            if line and any(w in line.lower() for w in ['warning', 'warn', 'deprecated']):
                warnings.append(line)
        return warnings


__all__ = [
    "GeneratorLanguage",
    "GenerationResult",
    "GeneratorConfig",
    "ExternalGenerator",
    "ExternalGeneratorError",
    "GeneratorNotInstalledError",
    "GeneratorExecutionError",
]
