"""
oapi-codegen Integration.

Uses oapi-codegen to generate Go client/server code.
https://github.com/oapi-codegen/oapi-codegen

Requirements:
- Go 1.21+
- oapi-codegen CLI
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


class OapiCodegenGenerator(ExternalGenerator):
    """
    oapi-codegen - Go OpenAPI Generator.

    Generates Go client and server code using oapi-codegen.
    Supports Chi, Echo, Fiber, Gin, and net/http.

    Usage:
        generator = OapiCodegenGenerator()
        result = generator.generate(
            spec_path=Path("openapi.yaml"),
            output_dir=Path("internal/api"),
            config=GeneratorConfig(
                go_package="api",
                go_generate_client=True,
                go_generate_models=True,
            )
        )
    """

    @property
    def language(self) -> GeneratorLanguage:
        return GeneratorLanguage.GO

    @property
    def name(self) -> str:
        return "oapi-codegen"

    @property
    def cli_command(self) -> str:
        return "oapi-codegen"

    @property
    def version_command(self) -> list[str]:
        return [self.cli_command, "--version"]

    def install_instructions(self) -> str:
        return """
oapi-codegen Installation:

Option 1: Go install (recommended)
    go install github.com/oapi-codegen/oapi-codegen/v2/cmd/oapi-codegen@latest

Option 2: Homebrew
    brew install oapi-codegen

Option 3: Download binary
    https://github.com/oapi-codegen/oapi-codegen/releases

After installation, ensure it's in your PATH:
    oapi-codegen --version

Documentation:
    https://github.com/oapi-codegen/oapi-codegen
"""

    def _build_command(
        self,
        spec_path: Path,
        output_dir: Path,
        config: GeneratorConfig | None = None,
    ) -> list[str]:
        """Build the oapi-codegen command."""
        config = config or GeneratorConfig()

        # Create config file for complex options
        config_file = self._create_config_file(output_dir, config)

        command = [
            self.cli_command,
            "-config", str(config_file),
            str(spec_path),
        ]

        return command

    def _create_config_file(
        self,
        output_dir: Path,
        config: GeneratorConfig,
    ) -> Path:
        """Create oapi-codegen YAML config file."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        config_file = output_dir / "oapi-codegen.yaml"

        # Build generate section
        generate = {}
        if config.go_generate_client:
            generate["client"] = True
        if config.go_generate_models:
            generate["models"] = True

        # Add server framework if specified
        if config.go_server_framework:
            framework_map = {
                "chi": "chi-server",
                "echo": "echo-server",
                "fiber": "fiber-server",
                "gin": "gin-server",
                "net-http": "std-http-server",
            }
            server_key = framework_map.get(config.go_server_framework)
            if server_key:
                generate[server_key] = True

        # Build config
        package_name = config.go_package or config.package_name or "api"
        output_filename = f"{package_name}.gen.go"

        yaml_config = {
            "package": package_name,
            "output": str(output_dir / output_filename),
            "generate": generate,
        }

        # Write config file
        config_file.write_text(yaml.dump(yaml_config, default_flow_style=False))

        return config_file

    def _get_file_extensions(self) -> list[str]:
        return [".go"]

    def generate_with_go_generate(
        self,
        spec_path: Path,
        output_dir: Path,
        package_name: str = "api",
    ) -> str:
        """
        Generate a go:generate directive for embedding in Go code.

        Args:
            spec_path: Path to OpenAPI spec
            output_dir: Output directory
            package_name: Go package name

        Returns:
            go:generate directive string
        """
        return (
            f"//go:generate oapi-codegen "
            f"-package {package_name} "
            f"-generate types,client "
            f"-o {output_dir}/{package_name}.gen.go "
            f"{spec_path}"
        )


__all__ = ["OapiCodegenGenerator"]
