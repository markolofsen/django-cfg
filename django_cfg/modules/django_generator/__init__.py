"""django_generator — unified codegen module.

Combines:
  - Internal pipeline (drf-spectacular slicer + external CLIs + ts_extras)
  - User-facing config (Config/OpenAPI/Target/...) — was django_codegen
  - Codegen runner (orchestrator with copy_groups, post_build, wildcards)
  - FastAPI ORM generator (was django_fastapi)
"""

default_app_config = "django_cfg.modules.django_generator.apps.DjangoGeneratorConfig"

# Internal pipeline (drf-spectacular → slicer → external CLIs)
from .openapi.pipeline.config import (
    OpenAPIConfig,
    OpenAPIGroupConfig,
    GenerationTarget,
    RunReport,
)
from .openapi.service import (
    DjangoOpenAPI,
    get_openapi_service,
)
from .urls import get_openapi_urls

# User-facing config (replaces django_codegen public surface)
from .public.config import (
    Platform,
    Language,
    TargetType,
    ORMGenerator,
    Target,
    ExtensionTarget,
    ORMTarget,
    Config,
    OpenAPI,
    Centrifugo,
    SDK,
    SDKPackage,
    ORM,
    GeneratorOptions,
)

# Codegen runner + inspector
from .openapi.runner import run, run_with_options
from .public.inspector import (
    inspect_config,
    ConfigSummary,
    TargetSummary,
    ExtensionsSummary,
    SDKPackageSummary,
    ORMTargetSummary,
)

__all__ = [
    # Internal pipeline
    "OpenAPIConfig",
    "OpenAPIGroupConfig",
    "GenerationTarget",
    "RunReport",
    "DjangoOpenAPI",
    "get_openapi_service",
    "get_openapi_urls",
    # User config
    "Platform",
    "Language",
    "TargetType",
    "ORMGenerator",
    "Target",
    "ExtensionTarget",
    "ORMTarget",
    "Config",
    "OpenAPI",
    "Centrifugo",
    "SDK",
    "SDKPackage",
    "ORM",
    "GeneratorOptions",
    # Runner
    "run",
    "run_with_options",
    # Inspector
    "inspect_config",
    "ConfigSummary",
    "TargetSummary",
    "ExtensionsSummary",
    "SDKPackageSummary",
    "ORMTargetSummary",
]
