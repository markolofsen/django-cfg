"""
Code Generators - IR → Python/TypeScript clients.

This package provides generators for converting IR to language-specific clients.

Usage:
    >>> from django_cfg.modules.django_client.core.generator import generate_python, generate_typescript
    >>> from django_cfg.modules.django_client.core.parser import parse_openapi
    >>>
    >>> # Parse OpenAPI spec
    >>> context = parse_openapi(spec_dict)
    >>>
    >>> # Generate Python client
    >>> python_files = generate_python(context)
    >>> for file in python_files:
    ...     print(f"{file.path}: {len(file.content)} bytes")
    >>>
    >>> # Generate TypeScript client
    >>> ts_files = generate_typescript(context)
"""

from pathlib import Path
from typing import Literal

from ..ir import IRContext
from .base import GeneratedFile
from .claude_generator import ClaudeGenerator
from .go import GoGenerator
from .proto import ProtoGenerator
from .python import PythonGenerator
from .typescript import TypeScriptGenerator
from .swift_codable import SwiftCodableGenerator

__all__ = [
    "PythonGenerator",
    "TypeScriptGenerator",
    "GoGenerator",
    "ProtoGenerator",
    "SwiftCodableGenerator",
    "ClaudeGenerator",
    "GeneratedFile",
    "generate_python",
    "generate_typescript",
    "generate_go",
    "generate_proto",
    "generate_swift_codable",
    "generate_client",
]


def generate_python(context: IRContext, output_dir: Path | None = None) -> list[GeneratedFile]:
    """
    Generate Python client from IR.

    Args:
        context: IRContext from parser
        output_dir: Optional output directory (saves files if provided)

    Returns:
        List of GeneratedFile objects

    Examples:
        >>> files = generate_python(context)
        >>> # Or save directly
        >>> files = generate_python(context, output_dir=Path("./generated/python"))
    """
    generator = PythonGenerator(context)
    files = generator.generate()

    if output_dir:
        generator.save_files(files, output_dir)

    return files


def generate_typescript(context: IRContext, output_dir: Path | None = None) -> list[GeneratedFile]:
    """
    Generate TypeScript client from IR.

    Args:
        context: IRContext from parser
        output_dir: Optional output directory (saves files if provided)

    Returns:
        List of GeneratedFile objects

    Examples:
        >>> files = generate_typescript(context)
        >>> # Or save directly
        >>> files = generate_typescript(context, output_dir=Path("./generated/typescript"))
    """
    generator = TypeScriptGenerator(context)
    files = generator.generate()

    if output_dir:
        generator.save_files(files, output_dir)

    return files


def generate_go(context: IRContext, output_dir: Path | None = None, **kwargs) -> list[GeneratedFile]:
    """
    Generate Go client from IR.

    Args:
        context: IRContext from parser
        output_dir: Optional output directory (saves files if provided)
        **kwargs: Additional options (client_structure, package_config, etc.)

    Returns:
        List of GeneratedFile objects

    Examples:
        >>> files = generate_go(context)
        >>> # Or save directly
        >>> files = generate_go(context, output_dir=Path("./generated/go"))
        >>> # With custom package config
        >>> files = generate_go(
        ...     context,
        ...     package_config={"module_name": "github.com/user/api-client"},
        ...     generate_package_files=True
        ... )
    """
    generator = GoGenerator(context, **kwargs)
    files = generator.generate()

    if output_dir:
        generator.save_files(files, output_dir)

    return files


def generate_proto(context: IRContext, output_dir: Path | None = None, **kwargs) -> list[GeneratedFile]:
    """
    Generate Protocol Buffer definitions from IR.

    Args:
        context: IRContext from parser
        output_dir: Optional output directory (saves files if provided)
        **kwargs: Additional options (split_files, package_name, etc.)

    Returns:
        List of GeneratedFile objects

    Examples:
        >>> files = generate_proto(context)
        >>> # Or save directly
        >>> files = generate_proto(context, output_dir=Path("./generated/proto"))
        >>> # With custom settings
        >>> files = generate_proto(
        ...     context,
        ...     split_files=False,  # Single api.proto file
        ...     package_name="myapi.v1"
        ... )
    """
    generator = ProtoGenerator(context, **kwargs)
    files = generator.generate()

    if output_dir:
        generator.save_files(files, output_dir)

    return files


def generate_swift_codable(context: IRContext, output_dir: Path | None = None, **kwargs) -> list[GeneratedFile]:
    """
    Generate Swift Codable types from IR.

    Args:
        context: IRContext from parser
        output_dir: Optional output directory (saves files if provided)
        **kwargs: Additional options (generate_endpoints, generate_models, group_name)

    Returns:
        List of GeneratedFile objects

    Examples:
        >>> files = generate_swift_codable(context)
        >>> # Or save directly
        >>> files = generate_swift_codable(context, output_dir=Path("./generated/swift"))
        >>> # With group name
        >>> files = generate_swift_codable(
        ...     context,
        ...     output_dir=Path("./generated/swift"),
        ...     group_name="workspaces"
        ... )
    """
    generator = SwiftCodableGenerator(context, **kwargs)
    files = generator.generate()

    if output_dir:
        generator.save_files(files, output_dir)

    return files


def generate_client(
    context: IRContext,
    language: Literal["python", "typescript", "go", "proto", "swift_codable"],
    output_dir: Path | None = None,
    **kwargs,
) -> list[GeneratedFile]:
    """
    Generate client for specified language.

    Args:
        context: IRContext from parser
        language: Target language ('python', 'typescript', 'go', 'proto', or 'swift_codable')
        output_dir: Optional output directory
        **kwargs: Additional language-specific options

    Returns:
        List of GeneratedFile objects

    Examples:
        >>> files = generate_client(context, "python")
        >>> files = generate_client(context, "typescript", Path("./generated"))
        >>> files = generate_client(context, "go", Path("./generated"), generate_package_files=True)
        >>> files = generate_client(context, "proto", Path("./generated"), split_files=False)
        >>> files = generate_client(context, "swift_codable", Path("./generated"))
    """
    if language == "python":
        return generate_python(context, output_dir)
    elif language == "typescript":
        return generate_typescript(context, output_dir)
    elif language == "go":
        return generate_go(context, output_dir, **kwargs)
    elif language == "proto":
        return generate_proto(context, output_dir, **kwargs)
    elif language == "swift_codable":
        return generate_swift_codable(context, output_dir, **kwargs)
    else:
        raise ValueError(f"Unsupported language: {language}")
