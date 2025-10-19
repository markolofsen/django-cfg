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
from .python import PythonGenerator
from .typescript import TypeScriptGenerator

__all__ = [
    "PythonGenerator",
    "TypeScriptGenerator",
    "GeneratedFile",
    "generate_python",
    "generate_typescript",
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


def generate_client(
    context: IRContext,
    language: Literal["python", "typescript"],
    output_dir: Path | None = None,
) -> list[GeneratedFile]:
    """
    Generate client for specified language.

    Args:
        context: IRContext from parser
        language: Target language ('python' or 'typescript')
        output_dir: Optional output directory

    Returns:
        List of GeneratedFile objects

    Examples:
        >>> files = generate_client(context, "python")
        >>> files = generate_client(context, "typescript", Path("./generated"))
    """
    if language == "python":
        return generate_python(context, output_dir)
    elif language == "typescript":
        return generate_typescript(context, output_dir)
    else:
        raise ValueError(f"Unsupported language: {language}")
