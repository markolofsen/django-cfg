"""
openapi-python-client Integration.

Uses openapi-python-client to generate Python client code.
https://github.com/openapi-generators/openapi-python-client

Requirements:
- Python 3.10+
- openapi-python-client package
"""

from __future__ import annotations

import yaml
from pathlib import Path
from typing import TYPE_CHECKING

from .base import (
    ExternalGenerator,
    GeneratorLanguage,
    GeneratorConfig,
)

if TYPE_CHECKING:
    pass


class OpenAPIPythonClientGenerator(ExternalGenerator):
    """
    openapi-python-client - Modern Python OpenAPI Generator.

    Generates type-safe Python clients using dataclasses and type hints.

    Usage:
        generator = OpenAPIPythonClientGenerator()
        result = generator.generate(
            spec_path=Path("openapi.yaml"),
            output_dir=Path("clients/python"),
            config=GeneratorConfig(
                python_project_name="my-api-client",
                python_package_name="my_api",
            )
        )
    """

    @property
    def language(self) -> GeneratorLanguage:
        return GeneratorLanguage.PYTHON

    @property
    def name(self) -> str:
        return "openapi-python-client"

    @property
    def cli_command(self) -> str:
        return "openapi-python-client"

    @property
    def version_command(self) -> list[str]:
        return [self.cli_command, "--version"]

    def install_instructions(self) -> str:
        return """
openapi-python-client Installation:

Option 1: pip (recommended)
    pip install openapi-python-client

Option 2: pipx (isolated installation)
    pipx install openapi-python-client

Option 3: uv
    uv tool install openapi-python-client

After installation, verify:
    openapi-python-client --version

Requirements:
    - Python 3.10 or higher

Documentation:
    https://github.com/openapi-generators/openapi-python-client
"""

    def _build_command(
        self,
        spec_path: Path,
        output_dir: Path,
        config: GeneratorConfig | None = None,
    ) -> list[str]:
        """Build the openapi-python-client command."""
        config = config or GeneratorConfig()

        command = [
            self.cli_command,
            "generate",
            "--path", str(spec_path),
            "--output-path", str(output_dir),
        ]

        # Use config file if we have custom options
        if self._needs_config_file(config):
            config_file = self._create_config_file(output_dir, config)
            command.extend(["--config", str(config_file)])

        # Overwrite existing files
        command.append("--overwrite")

        # Extra arguments
        if config.extra_args:
            command.extend(config.extra_args)

        return command

    def _needs_config_file(self, config: GeneratorConfig) -> bool:
        """Check if we need a config file for these options."""
        return bool(
            config.python_project_name or
            config.python_package_name or
            config.package_name
        )

    def _create_config_file(
        self,
        output_dir: Path,
        config: GeneratorConfig,
    ) -> Path:
        """Create openapi-python-client config file."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        config_file = output_dir / "openapi-python-client-config.yaml"

        yaml_config = {}

        if config.python_project_name or config.package_name:
            yaml_config["project_name_override"] = (
                config.python_project_name or config.package_name
            )

        if config.python_package_name or config.package_name:
            package_name = config.python_package_name or config.package_name
            # Python packages use underscores, not hyphens
            yaml_config["package_name_override"] = package_name.replace("-", "_")

        # Write config file
        config_file.write_text(yaml.dump(yaml_config, default_flow_style=False))

        return config_file

    def _get_file_extensions(self) -> list[str]:
        return [".py"]

    def generate_from_url(
        self,
        url: str,
        output_dir: Path,
        config: GeneratorConfig | None = None,
        *,
        timeout: int = 300,
    ) -> "GenerationResult":
        """
        Generate client from a URL instead of a local file.

        Args:
            url: URL to OpenAPI spec (JSON or YAML)
            output_dir: Directory for generated output
            config: Optional configuration
            timeout: Maximum execution time in seconds

        Returns:
            GenerationResult with success status
        """
        import subprocess
        import time
        from .base import GenerationResult

        start_time = time.monotonic()
        config = config or GeneratorConfig()
        output_dir = Path(output_dir).resolve()
        output_dir.mkdir(parents=True, exist_ok=True)

        command = [
            self.cli_command,
            "generate",
            "--url", url,
            "--output-path", str(output_dir),
            "--overwrite",
        ]

        if self._needs_config_file(config):
            config_file = self._create_config_file(output_dir, config)
            command.extend(["--config", str(config_file)])

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

            files = self._collect_generated_files(output_dir)

            return GenerationResult(
                success=True,
                language=self.language,
                output_dir=output_dir,
                files_generated=files,
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


# Import for type hints in generate_from_url
from .base import GenerationResult  # noqa: E402


__all__ = ["OpenAPIPythonClientGenerator"]
