"""
Internal Code Generators.

Built-in generators for TypeScript, Python, Go, and Proto.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from django_cfg.modules.django_client.core.ir import IRContext
    from django_cfg.modules.django_client.core.config import OpenAPIConfig


class InternalGenerators:
    """
    Facade for internal code generators.

    Usage:
        generators = InternalGenerators(ir_context, openapi_schema, config)
        files = generators.generate_typescript(output_dir, group_name)
    """

    def __init__(
        self,
        ir_context: "IRContext",
        openapi_schema: dict,
        config: "OpenAPIConfig",
        *,
        tag_prefix: str = "",
        group_name: str = "",
        log: Callable[[str], None] | None = None,
    ):
        self.ir_context = ir_context
        self.openapi_schema = openapi_schema
        self.config = config
        self.tag_prefix = tag_prefix
        self.group_name = group_name
        self.log = log or (lambda msg: None)

    def generate_python(self, output_dir: Path) -> list[Path]:
        """Generate Python client using built-in generator."""
        from django_cfg.modules.django_client.core.generator import PythonGenerator

        output_dir.mkdir(parents=True, exist_ok=True)

        generator = PythonGenerator(
            self.ir_context,
            client_structure=self.config.client_structure,
            openapi_schema=self.openapi_schema,
            tag_prefix=self.tag_prefix,
            generate_package_files=self.config.generate_package_files,
            group_name=self.group_name,
        )

        files = generator.generate()
        generated_paths = []

        for generated_file in files:
            full_path = output_dir / generated_file.path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(generated_file.content)
            generated_paths.append(full_path)

        return generated_paths

    def generate_typescript(self, output_dir: Path) -> list[Path]:
        """Generate TypeScript client using built-in generator."""
        from django_cfg.modules.django_client.core.generator import TypeScriptGenerator

        output_dir.mkdir(parents=True, exist_ok=True)

        generator = TypeScriptGenerator(
            self.ir_context,
            client_structure=self.config.client_structure,
            openapi_schema=self.openapi_schema,
            tag_prefix=self.tag_prefix,
            generate_package_files=self.config.generate_package_files,
            generate_zod_schemas=self.config.generate_zod_schemas,
            generate_fetchers=self.config.generate_fetchers,
            generate_swr_hooks=self.config.generate_swr_hooks,
            group_name=self.group_name,
        )

        files = generator.generate()
        generated_paths = []

        for generated_file in files:
            full_path = output_dir / generated_file.path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(generated_file.content)
            generated_paths.append(full_path)

        return generated_paths

    def generate_go(self, output_dir: Path) -> list[Path]:
        """Generate Go client using built-in generator."""
        from django_cfg.modules.django_client.core.generator import GoGenerator

        output_dir.mkdir(parents=True, exist_ok=True)

        generator = GoGenerator(
            self.ir_context,
            client_structure=self.config.client_structure,
            openapi_schema=self.openapi_schema,
            tag_prefix=self.tag_prefix,
            generate_package_files=self.config.generate_package_files,
            package_config={
                "name": self.group_name,
                "module_name": self.group_name,
                "version": "v1.0.0",
            },
            group_name=self.group_name,
        )

        files = generator.generate()
        generated_paths = []

        for generated_file in files:
            full_path = output_dir / generated_file.path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(generated_file.content)
            generated_paths.append(full_path)

        return generated_paths

    def generate_proto(self, output_dir: Path) -> list[Path]:
        """Generate Protocol Buffer definitions using built-in generator."""
        from django_cfg.modules.django_client.core.generator import ProtoGenerator

        output_dir.mkdir(parents=True, exist_ok=True)

        generator = ProtoGenerator(
            self.ir_context,
            split_files=True,
            package_name=f"{self.group_name}.v1",
            group_name=self.group_name,
        )

        files = generator.generate()
        generated_paths = []

        for generated_file in files:
            full_path = output_dir / generated_file.path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(generated_file.content)
            generated_paths.append(full_path)

        return generated_paths

    def generate_swift_codable(self, output_dir: Path) -> list[Path]:
        """Generate Swift Codable types using built-in generator."""
        from django_cfg.modules.django_client.core.generator import SwiftCodableGenerator

        output_dir.mkdir(parents=True, exist_ok=True)

        generator = SwiftCodableGenerator(
            self.ir_context,
            generate_endpoints=True,
            generate_models=True,
            group_name=self.group_name,
        )

        files = generator.generate()
        generated_paths = []

        for generated_file in files:
            full_path = output_dir / generated_file.path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(generated_file.content)
            generated_paths.append(full_path)

        return generated_paths

    @staticmethod
    def generate_swift_codable_shared(output_dir: Path) -> list[Path]:
        """
        Generate shared Swift Codable files (JSONValue, etc.).

        Should be called once after all groups are generated.
        """
        from django_cfg.modules.django_client.core.generator import SwiftCodableGenerator

        output_dir.mkdir(parents=True, exist_ok=True)

        files = SwiftCodableGenerator.generate_shared_files()
        generated_paths = []

        for generated_file in files:
            full_path = output_dir / generated_file.path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(generated_file.content)
            generated_paths.append(full_path)

        return generated_paths


__all__ = ["InternalGenerators"]
