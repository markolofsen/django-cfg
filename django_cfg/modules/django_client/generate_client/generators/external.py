"""
External Code Generators.

Integrations with external CLI tools:
- Swift: apple/swift-openapi-generator
- Go: oapi-codegen
- Python: openapi-python-client
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from django_cfg.modules.django_client.core.external import (
        GenerationResult,
        GeneratorConfig,
    )


class ExternalGenerators:
    """
    Facade for external CLI-based code generators.

    Usage:
        generators = ExternalGenerators(spec_path, log=print)

        # Check installation
        if not generators.is_swift_available():
            print(generators.get_swift_install_instructions())
            return

        # Generate
        result = generators.generate_swift(output_dir)
        if result.success:
            print(f"Generated {len(result.files_generated)} files")
    """

    def __init__(
        self,
        spec_path: Path,
        *,
        log: Callable[[str], None] | None = None,
    ):
        self.spec_path = Path(spec_path)
        self.log = log or (lambda msg: None)

        # Lazy-loaded generators
        self._swift_gen = None
        self._go_gen = None
        self._python_gen = None

    @property
    def swift_generator(self):
        """Get Swift generator instance."""
        if self._swift_gen is None:
            from django_cfg.modules.django_client.core.external import SwiftOpenAPIGenerator
            self._swift_gen = SwiftOpenAPIGenerator()
        return self._swift_gen

    @property
    def go_generator(self):
        """Get Go generator instance."""
        if self._go_gen is None:
            from django_cfg.modules.django_client.core.external import OapiCodegenGenerator
            self._go_gen = OapiCodegenGenerator()
        return self._go_gen

    @property
    def python_generator(self):
        """Get Python generator instance."""
        if self._python_gen is None:
            from django_cfg.modules.django_client.core.external import OpenAPIPythonClientGenerator
            self._python_gen = OpenAPIPythonClientGenerator()
        return self._python_gen

    # Installation checks

    def is_swift_available(self) -> bool:
        """Check if Swift generator is installed."""
        return self.swift_generator.check_installation()

    def is_go_available(self) -> bool:
        """Check if Go generator (oapi-codegen) is installed."""
        return self.go_generator.check_installation()

    def is_python_available(self) -> bool:
        """Check if Python generator (openapi-python-client) is installed."""
        return self.python_generator.check_installation()

    def check_all(self) -> dict[str, bool]:
        """Check all external generators."""
        return {
            "swift": self.is_swift_available(),
            "go": self.is_go_available(),
            "python": self.is_python_available(),
        }

    # Installation instructions

    def get_swift_install_instructions(self) -> str:
        """Get Swift generator installation instructions."""
        return self.swift_generator.install_instructions()

    def get_go_install_instructions(self) -> str:
        """Get Go generator installation instructions."""
        return self.go_generator.install_instructions()

    def get_python_install_instructions(self) -> str:
        """Get Python generator installation instructions."""
        return self.python_generator.install_instructions()

    # Generation methods

    def generate_swift(
        self,
        output_dir: Path,
        config: "GeneratorConfig | None" = None,
    ) -> "GenerationResult":
        """
        Generate Swift client using apple/swift-openapi-generator.

        Args:
            output_dir: Directory for generated output
            config: Optional generator configuration

        Returns:
            GenerationResult with success status and file list
        """
        from django_cfg.modules.django_client.core.external import (
            GeneratorConfig,
            GeneratorNotInstalledError,
        )

        config = config or GeneratorConfig()

        self.log(f"  → Generating Swift client (apple/swift-openapi-generator)...")

        try:
            result = self.swift_generator.generate(
                spec_path=self.spec_path,
                output_dir=output_dir,
                config=config,
            )

            if result.success:
                self.log(f"  ✅ Swift client: {output_dir} ({len(result.files_generated)} files)")
            else:
                self.log(f"  ❌ Swift generation failed: {result.error}")

            return result

        except GeneratorNotInstalledError as e:
            self.log(f"  ❌ Swift generator not installed")
            self.log(e.install_instructions)
            raise

    def generate_go(
        self,
        output_dir: Path,
        config: "GeneratorConfig | None" = None,
    ) -> "GenerationResult":
        """
        Generate Go client using oapi-codegen.

        Args:
            output_dir: Directory for generated output
            config: Optional generator configuration

        Returns:
            GenerationResult with success status and file list
        """
        from django_cfg.modules.django_client.core.external import (
            GeneratorConfig,
            GeneratorNotInstalledError,
        )

        config = config or GeneratorConfig()

        self.log(f"  → Generating Go client (oapi-codegen)...")

        try:
            result = self.go_generator.generate(
                spec_path=self.spec_path,
                output_dir=output_dir,
                config=config,
            )

            if result.success:
                self.log(f"  ✅ Go client: {output_dir} ({len(result.files_generated)} files)")
            else:
                self.log(f"  ❌ Go generation failed: {result.error}")

            return result

        except GeneratorNotInstalledError as e:
            self.log(f"  ❌ oapi-codegen not installed")
            self.log(e.install_instructions)
            raise

    def generate_python(
        self,
        output_dir: Path,
        config: "GeneratorConfig | None" = None,
    ) -> "GenerationResult":
        """
        Generate Python client using openapi-python-client.

        Args:
            output_dir: Directory for generated output
            config: Optional generator configuration

        Returns:
            GenerationResult with success status and file list
        """
        from django_cfg.modules.django_client.core.external import (
            GeneratorConfig,
            GeneratorNotInstalledError,
        )

        config = config or GeneratorConfig()

        self.log(f"  → Generating Python client (openapi-python-client)...")

        try:
            result = self.python_generator.generate(
                spec_path=self.spec_path,
                output_dir=output_dir,
                config=config,
            )

            if result.success:
                self.log(f"  ✅ Python client: {output_dir} ({len(result.files_generated)} files)")
            else:
                self.log(f"  ❌ Python generation failed: {result.error}")

            return result

        except GeneratorNotInstalledError as e:
            self.log(f"  ❌ openapi-python-client not installed")
            self.log(e.install_instructions)
            raise


__all__ = ["ExternalGenerators"]
