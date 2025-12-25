"""
Generation Configuration.

Holds all configuration for client generation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django_cfg.modules.django_client.core.config import OpenAPIConfig


@dataclass
class LanguageOptions:
    """Options for which languages to generate."""
    python: bool = True
    typescript: bool = True
    go: bool = True
    proto: bool = True
    swift: bool = False
    swift_codable: bool = False  # Simple Codable types (no OpenAPIRuntime)

    # External generator flags
    external_go: bool = False
    external_python: bool = False

    @classmethod
    def from_options(cls, options: dict) -> "LanguageOptions":
        """Create from Django command options."""
        # Check if a single language is specified
        single_python = options.get("python") and not options.get("typescript") and not options.get("go") and not options.get("proto") and not options.get("swift") and not options.get("swift_codable")
        single_typescript = options.get("typescript") and not options.get("python") and not options.get("go") and not options.get("proto") and not options.get("swift") and not options.get("swift_codable")
        single_go = options.get("go") and not options.get("python") and not options.get("typescript") and not options.get("proto") and not options.get("swift") and not options.get("swift_codable")
        single_proto = options.get("proto") and not options.get("python") and not options.get("typescript") and not options.get("go") and not options.get("swift") and not options.get("swift_codable")
        single_swift = options.get("swift") and not options.get("python") and not options.get("typescript") and not options.get("go") and not options.get("proto") and not options.get("swift_codable")
        single_swift_codable = options.get("swift_codable") and not options.get("python") and not options.get("typescript") and not options.get("go") and not options.get("proto") and not options.get("swift")

        if single_python:
            return cls(python=True, typescript=False, go=False, proto=False, swift=False, swift_codable=False)
        elif single_typescript:
            return cls(python=False, typescript=True, go=False, proto=False, swift=False, swift_codable=False)
        elif single_go:
            return cls(python=False, typescript=False, go=True, proto=False, swift=False, swift_codable=False)
        elif single_proto:
            return cls(python=False, typescript=False, go=False, proto=True, swift=False, swift_codable=False)
        elif single_swift:
            return cls(python=False, typescript=False, go=False, proto=False, swift=True, swift_codable=False)
        elif single_swift_codable:
            return cls(python=False, typescript=False, go=False, proto=False, swift=False, swift_codable=True)
        else:
            return cls(
                python=not options.get("no_python", False),
                typescript=not options.get("no_typescript", False),
                go=not options.get("no_go", False),
                proto=not options.get("no_proto", False),
                swift=options.get("swift", False),
                swift_codable=options.get("swift_codable", False),
                external_go=options.get("external_go", False),
                external_python=options.get("external_python", False),
            )


@dataclass
class GenerationConfig:
    """Configuration for client generation."""
    # Groups to generate
    groups: list[str] = field(default_factory=list)

    # Language options
    languages: LanguageOptions = field(default_factory=LanguageOptions)

    # Behavior flags
    dry_run: bool = False
    no_build: bool = False
    copy_cfg_clients: bool = False
    skip_nextjs_copy: bool = False
    verbose: bool = False

    # Service config reference
    openapi_config: "OpenAPIConfig | None" = None

    @classmethod
    def from_options(cls, options: dict, openapi_config: "OpenAPIConfig | None" = None) -> "GenerationConfig":
        """Create from Django command options."""
        return cls(
            groups=options.get("groups") or [],
            languages=LanguageOptions.from_options(options),
            dry_run=options.get("dry_run", False),
            no_build=options.get("no_build", False),
            copy_cfg_clients=options.get("copy_cfg_clients", False),
            skip_nextjs_copy=options.get("skip_nextjs_copy", False),
            verbose=options.get("verbose", False),
            openapi_config=openapi_config,
        )


@dataclass
class GenerationResult:
    """Result of generating a single group."""
    group_name: str
    success: bool
    error: str | None = None

    # Generated file counts
    python_files: int = 0
    typescript_files: int = 0
    go_files: int = 0
    proto_files: int = 0
    swift_files: int = 0
    swift_codable_files: int = 0

    # Paths
    schema_path: Path | None = None


__all__ = ["LanguageOptions", "GenerationConfig", "GenerationResult"]
