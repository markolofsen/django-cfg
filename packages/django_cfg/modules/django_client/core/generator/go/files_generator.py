"""
Files Generator - Generates auxiliary files (go.mod, README, Makefile, etc.).
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from jinja2 import Environment

    from ...ir import IRContext
    from ..base import GeneratedFile
    from .generator import GoGenerator


class FilesGenerator:
    """Generates auxiliary files for Go client."""

    def __init__(
        self,
        jinja_env: Environment,
        context: IRContext,
        generator: GoGenerator,
    ):
        """Initialize files generator."""
        self.jinja_env = jinja_env
        self.context = context
        self.generator = generator

    def generate_go_mod(self) -> GeneratedFile:
        """Generate go.mod file."""
        template = self.jinja_env.get_template("go.mod.j2")

        module_name = self.generator.package_config.get("module_name", "apiclient")
        go_version = self.generator.package_config.get("go_version", "1.21")

        content = template.render(
            module_name=module_name,
            go_version=go_version,
            generated_at=datetime.now().isoformat(),
        )

        return self.generator._create_generated_file(
            path="go.mod",
            content=content,
            description="Go module definition"
        )

    def generate_readme(self) -> GeneratedFile:
        """Generate README.md file."""
        template = self.jinja_env.get_template("README.md.j2")

        content = template.render(
            module_name=self.generator.package_config.get("module_name", "apiclient"),
            api_title=self.context.openapi_info.title if self.context.openapi_info else "API Client",
            api_version=self.context.openapi_info.api_version if self.context.openapi_info else "1.0.0",
            generated_at=datetime.now().isoformat(),
        )

        return self.generator._create_generated_file(
            path="README.md",
            content=content,
            description="Usage documentation"
        )

    def generate_makefile(self) -> GeneratedFile:
        """Generate Makefile."""
        template = self.jinja_env.get_template("Makefile.j2")

        content = template.render(
            generated_at=datetime.now().isoformat(),
        )

        return self.generator._create_generated_file(
            path="Makefile",
            content=content,
            description="Build automation"
        )

    def generate_errors_file(self, shared: bool = False) -> GeneratedFile:
        """
        Generate errors.go with API error handling.

        Args:
            shared: If True, generate in shared/ package for namespaced structure
        """
        template = self.jinja_env.get_template("errors.go.j2")

        package_name = "shared" if shared else self.generator.package_name
        path = "shared/errors.go" if shared else "errors.go"

        content = template.render(
            package_name=package_name,
            generated_at=datetime.now().isoformat(),
        )

        return self.generator._create_generated_file(
            path=path,
            content=content,
            description="API error types"
        )

    def generate_middleware_file(self) -> GeneratedFile:
        """Generate middleware.go with retry, logging, rate limiting."""
        template = self.jinja_env.get_template("middleware.go.j2")

        content = template.render(
            package_name=self.generator.package_name,
            generated_at=datetime.now().isoformat(),
        )

        return self.generator._create_generated_file(
            path="middleware.go",
            content=content,
            description="HTTP middleware (retry, logging, rate limiting)"
        )

    def generate_validation_file(self) -> GeneratedFile:
        """Generate validation.go with client-side validation helpers."""
        template = self.jinja_env.get_template("validation.go.j2")

        content = template.render(
            package_name=self.generator.package_name,
            generated_at=datetime.now().isoformat(),
        )

        return self.generator._create_generated_file(
            path="validation.go",
            content=content,
            description="Client-side validation helpers"
        )
