"""
Apple Swift OpenAPI Generator Integration.

Uses apple/swift-openapi-generator to generate Swift client code.
https://github.com/apple/swift-openapi-generator

Requirements:
- Swift 5.9+
- swift-openapi-generator CLI or SPM plugin
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from .base import (
    ExternalGenerator,
    GeneratorLanguage,
    GeneratorConfig,
)

if TYPE_CHECKING:
    pass


class SwiftOpenAPIGenerator(ExternalGenerator):
    """
    Apple Swift OpenAPI Generator.

    Generates Swift client code using the official Apple generator.
    Supports async/await, Sendable, and Codable protocols.

    Usage:
        generator = SwiftOpenAPIGenerator()
        result = generator.generate(
            spec_path=Path("openapi.yaml"),
            output_dir=Path("Sources/Generated"),
            config=GeneratorConfig(
                swift_access_modifier="public",
                swift_generate_types=True,
                swift_generate_client=True,
            )
        )
    """

    @property
    def language(self) -> GeneratorLanguage:
        return GeneratorLanguage.SWIFT

    @property
    def name(self) -> str:
        return "Apple Swift OpenAPI Generator"

    @property
    def cli_command(self) -> str:
        return "swift-openapi-generator"

    @property
    def version_command(self) -> list[str]:
        # swift-openapi-generator doesn't have --version, use --help instead
        return [self.cli_command, "--help"]

    def install_instructions(self) -> str:
        return """
Apple Swift OpenAPI Generator Installation:

Option 1: Homebrew (recommended for CLI usage)
    brew install swift-openapi-generator

Option 2: Mint
    mint install apple/swift-openapi-generator

Option 3: Build from source
    git clone https://github.com/apple/swift-openapi-generator.git
    cd swift-openapi-generator
    swift build -c release
    # Binary will be at .build/release/swift-openapi-generator

Option 4: Swift Package Plugin (for Xcode projects)
    Add to Package.swift:
    .package(url: "https://github.com/apple/swift-openapi-generator", from: "1.0.0")

Documentation:
    https://swiftpackageindex.com/apple/swift-openapi-generator/documentation
"""

    def _build_command(
        self,
        spec_path: Path,
        output_dir: Path,
        config: GeneratorConfig | None = None,
    ) -> list[str]:
        """Build the swift-openapi-generator command."""
        config = config or GeneratorConfig()

        command = [
            self.cli_command,
            "generate",
            str(spec_path),
            "--output-directory", str(output_dir),
        ]

        # Access modifier
        if config.swift_access_modifier:
            command.extend(["--access-modifier", config.swift_access_modifier])

        # What to generate (--mode must be specified separately for each mode)
        if config.swift_generate_types:
            command.extend(["--mode", "types"])
        if config.swift_generate_client:
            command.extend(["--mode", "client"])

        # Extra arguments
        if config.extra_args:
            command.extend(config.extra_args)

        return command

    def _get_file_extensions(self) -> list[str]:
        return [".swift"]

    def create_config_file(
        self,
        output_path: Path,
        config: GeneratorConfig | None = None,
    ) -> Path:
        """
        Create an openapi-generator-config.yaml file.

        This is useful for SPM plugin integration where config
        is read from a file rather than CLI args.

        Args:
            output_path: Directory to write config file
            config: Generator configuration

        Returns:
            Path to created config file
        """
        config = config or GeneratorConfig()
        output_path = Path(output_path)
        output_path.mkdir(parents=True, exist_ok=True)

        config_file = output_path / "openapi-generator-config.yaml"

        content = f"""# Auto-generated Swift OpenAPI Generator config
generate:
  - types
{"  - client" if config.swift_generate_client else ""}
accessModifier: {config.swift_access_modifier}
"""

        config_file.write_text(content)
        return config_file


__all__ = ["SwiftOpenAPIGenerator"]
