"""
Main runner entry point.

v6.0: Typed GeneratorOptions support.
v6.1: Rich logging integration.
v6.2: Platform enum instead of Language.
"""

from typing import Any

from django_cfg.modules.django_codegen.config import (
    Config,
    GeneratorOptions,
    Platform,
)
from django_cfg.modules.django_codegen.runner.centrifugo import run_centrifugo
from django_cfg.modules.django_codegen.runner.logger import (
    GenerationLogger,
    get_generation_logger,
    reset_generation_logger,
)
from django_cfg.modules.django_codegen.runner.openapi import run_openapi
from django_cfg.modules.django_codegen.runner.orm import run_orm
from django_cfg.modules.django_codegen.runner.sdk import run_sdk


def run(
    config: Config,
    *,
    # New typed interface (v6.0)
    options: GeneratorOptions | None = None,
    # Legacy interface (still supported)
    only_platforms: list[str] | None = None,
    only_target: str | None = None,
    only_groups: list[str] | None = None,
    dry_run: bool = False,
    stdout: Any = None,
    # New logging options (v6.1)
    verbose: bool = False,
    quiet: bool = False,
    logger: GenerationLogger | None = None,
) -> GenerationLogger:
    """
    Run generation based on config.

    Args:
        config: Generation config
        options: Typed generation options (v6.0). If provided, overrides legacy params.

        Legacy params (still supported):
        only_platforms: Filter to specific platforms (typescript, python, go, swift)
        only_target: Filter to specific target type (admin, packages, extensions, etc.)
        only_groups: Filter to specific groups
        dry_run: Preview without changes
        stdout: Django command stdout for output (deprecated, use logger)

        Logging options (v6.1):
        verbose: Show debug messages
        quiet: Only show errors
        logger: Custom GenerationLogger instance

    Returns:
        GenerationLogger with stats from this run

    Example (v6.0 - typed):
        from django_cfg.modules.django_codegen import (
            Config, OpenAPI, Target, Platform, TargetType, GeneratorOptions, run,
        )

        config = Config(openapi=OpenAPI(targets=[...]))
        options = GeneratorOptions(
            platforms={Platform.TYPESCRIPT},
            groups=["profiles"],
        )
        run(config, options=options)

    Example (legacy):
        run(config, only_platforms=["typescript"], only_groups=["profiles"])
    """
    # Convert typed options to legacy params if provided
    if options is not None:
        only_platforms = [p.value for p in options.platforms] if options.platforms else None
        only_groups = options.groups
        dry_run = options.dry_run
        verbose = options.verbose

    # Initialize logger
    if logger is None:
        reset_generation_logger()
        logger = get_generation_logger(verbose=verbose, quiet=quiet, reset=True)

    # Header
    logger.section_start("Code Generation")

    if dry_run:
        logger.warning("DRY RUN - no changes will be made")

    # Run generators (filtered by only_target if specified)
    run_openapi_gen = only_target is None or only_target not in ("orm",)
    run_centrifugo_gen = only_target is None or only_target not in ("orm",)
    run_sdk_gen = only_target is None or only_target not in ("orm",)
    run_orm_gen = only_target is None or only_target == "orm"

    if config.openapi and run_openapi_gen:
        run_openapi(config.openapi, only_platforms, only_target, only_groups, dry_run, logger)

    if config.centrifugo and run_centrifugo_gen:
        run_centrifugo(config.centrifugo, only_platforms, only_groups, dry_run, logger)

    if config.sdk and run_sdk_gen:
        run_sdk(config.sdk, only_groups, dry_run, logger)

    if config.orm and run_orm_gen:
        run_orm(config.orm, dry_run, logger)

    # Summary
    logger.summary()

    return logger


def run_with_options(
    config: Config,
    options: GeneratorOptions,
    logger: GenerationLogger | None = None,
) -> GenerationLogger:
    """
    Run generation with typed options.

    Convenience wrapper for the new typed interface.

    Example:
        from django_cfg.modules.django_codegen import (
            Config, GeneratorOptions, Language, run_with_options,
        )

        config = Config(...)
        options = GeneratorOptions(languages={Language.TYPESCRIPT})
        result = run_with_options(config, options)
        print(f"Generated {result.stats.groups_generated} groups")
    """
    return run(config, options=options, logger=logger)
