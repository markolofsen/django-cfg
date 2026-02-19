"""
Unified client generation module.

v6.0: Typed generation options, ORM support.
v6.2: Platform enum instead of Language.

Usage:
    from django_cfg.modules.django_codegen import (
        Config, OpenAPI, Target, ExtensionTarget,
        Platform, TargetType, GeneratorOptions,
    )

    # Configuration
    config = Config(
        openapi=OpenAPI(
            targets=[
                Target(
                    lang=Platform.TYPESCRIPT,
                    type=TargetType.ADMIN,
                    path=FRONTEND / "apps/admin/api/generated",
                    groups=["cfg_*", "profiles"],
                ),
            ],
        ),
    )

    # Programmatic generation with typed options
    options = GeneratorOptions(
        platforms={Platform.TYPESCRIPT, Platform.PYTHON},
        groups=["profiles"],
    )
    run(config, options=options)

CLI:
    python manage.py gen
    python manage.py gen --ts
    python manage.py gen --target admin
    python manage.py gen --list-targets
    python manage.py gen --groups profiles catalog
"""

from django_cfg.modules.django_codegen.config import (
    # Enums
    Platform,
    Language,  # Alias for backwards compatibility
    TargetType,
    ORMGenerator,
    # Target models
    Target,
    ExtensionTarget,
    ORMTarget,
    # Config models
    Config,
    OpenAPI,
    Centrifugo,
    SDK,
    SDKPackage,
    ORM,
    # Options
    GeneratorOptions,
)
from django_cfg.modules.django_codegen.runner import run, run_with_options

__all__ = [
    # Enums
    "Platform",
    "Language",  # Alias for backwards compatibility
    "TargetType",
    "ORMGenerator",
    # Target models
    "Target",
    "ExtensionTarget",
    "ORMTarget",
    # Config models
    "Config",
    "OpenAPI",
    "Centrifugo",
    "SDK",
    "SDKPackage",
    "ORM",
    # Options
    "GeneratorOptions",
    # Runner
    "run",
    "run_with_options",
]

default_app_config = "django_cfg.modules.django_codegen.apps.DjangoCodegenConfig"
