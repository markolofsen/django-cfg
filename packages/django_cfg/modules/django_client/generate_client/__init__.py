"""
Client Generation Module.

Provides modular client generation capabilities.

Usage:
    from django_cfg.modules.django_client.generate_client import (
        ClientGenerationOrchestrator,
        GenerationConfig,
    )

    # Create config from Django command options
    config = GenerationConfig.from_options(options, openapi_config)

    # Run generation
    orchestrator = ClientGenerationOrchestrator(service, config)
    results = orchestrator.generate_all()

Structure:
    generate_client/
    ├── __init__.py          # This file - exports
    ├── config.py            # Configuration dataclasses
    ├── orchestrator.py      # Main orchestration logic
    ├── generators/          # Code generators
    │   ├── internal.py      # Built-in generators (TS, Python, Go, Proto)
    │   └── external.py      # External CLI generators (Swift, oapi-codegen)
    └── utils/               # Utility modules
        ├── nextjs.py        # Next.js integration
        ├── typescript.py    # TypeScript type checking
        └── schema.py        # OpenAPI schema utilities
"""

from .config import GenerationConfig, GenerationResult, LanguageOptions
from .orchestrator import ClientGenerationOrchestrator
from .generators import InternalGenerators, ExternalGenerators
from .utils import NextJsUtils, TypeScriptUtils, SchemaUtils

__all__ = [
    # Config
    "GenerationConfig",
    "GenerationResult",
    "LanguageOptions",
    # Orchestrator
    "ClientGenerationOrchestrator",
    # Generators
    "InternalGenerators",
    "ExternalGenerators",
    # Utils
    "NextJsUtils",
    "TypeScriptUtils",
    "SchemaUtils",
]
