"""
External Code Generators.

This module provides integration with external CLI-based code generators
for Swift, Go, and Python.

Usage:
    from django_cfg.modules.django_client.core.external import (
        SwiftOpenAPIGenerator,
        OapiCodegenGenerator,
        OpenAPIPythonClientGenerator,
        GeneratorConfig,
    )

    # Swift
    swift_gen = SwiftOpenAPIGenerator()
    if swift_gen.check_installation():
        result = swift_gen.generate(
            spec_path=Path("openapi.yaml"),
            output_dir=Path("Sources/Generated"),
        )

    # Go
    go_gen = OapiCodegenGenerator()
    if go_gen.check_installation():
        result = go_gen.generate(
            spec_path=Path("openapi.yaml"),
            output_dir=Path("internal/api"),
            config=GeneratorConfig(go_package="api"),
        )

    # Python
    py_gen = OpenAPIPythonClientGenerator()
    if py_gen.check_installation():
        result = py_gen.generate(
            spec_path=Path("openapi.yaml"),
            output_dir=Path("clients/python"),
        )
"""

from .base import (
    GeneratorLanguage,
    GenerationResult,
    GeneratorConfig,
    ExternalGenerator,
    ExternalGeneratorError,
    GeneratorNotInstalledError,
    GeneratorExecutionError,
)
from .swift import SwiftOpenAPIGenerator
from .go import OapiCodegenGenerator
from .python import OpenAPIPythonClientGenerator


def get_generator(language: str | GeneratorLanguage) -> ExternalGenerator:
    """
    Get an external generator instance by language.

    Args:
        language: Target language ("swift", "go", "python")

    Returns:
        ExternalGenerator instance

    Raises:
        ValueError: If language is not supported
    """
    if isinstance(language, str):
        language = GeneratorLanguage(language.lower())

    generators = {
        GeneratorLanguage.SWIFT: SwiftOpenAPIGenerator,
        GeneratorLanguage.GO: OapiCodegenGenerator,
        GeneratorLanguage.PYTHON: OpenAPIPythonClientGenerator,
    }

    generator_class = generators.get(language)
    if generator_class is None:
        raise ValueError(
            f"Unsupported language: {language}. "
            f"Supported: {', '.join(g.value for g in GeneratorLanguage)}"
        )

    return generator_class()


def check_all_installations() -> dict[GeneratorLanguage, bool]:
    """
    Check which external generators are installed.

    Returns:
        Dict mapping language to installation status
    """
    return {
        GeneratorLanguage.SWIFT: SwiftOpenAPIGenerator().check_installation(),
        GeneratorLanguage.GO: OapiCodegenGenerator().check_installation(),
        GeneratorLanguage.PYTHON: OpenAPIPythonClientGenerator().check_installation(),
    }


def get_install_instructions(language: GeneratorLanguage) -> str:
    """
    Get installation instructions for a specific generator.

    Args:
        language: Target language

    Returns:
        Installation instructions string
    """
    return get_generator(language).install_instructions()


__all__ = [
    # Base classes
    "GeneratorLanguage",
    "GenerationResult",
    "GeneratorConfig",
    "ExternalGenerator",
    "ExternalGeneratorError",
    "GeneratorNotInstalledError",
    "GeneratorExecutionError",
    # Generators
    "SwiftOpenAPIGenerator",
    "OapiCodegenGenerator",
    "OpenAPIPythonClientGenerator",
    # Utilities
    "get_generator",
    "check_all_installations",
    "get_install_instructions",
]
