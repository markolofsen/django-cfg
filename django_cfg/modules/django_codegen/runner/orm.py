"""
ORM/FastAPI model generation runner.

Generates Pydantic/FastAPI models from Django ORM models.

v6.1: Rich logging integration.
v6.2: Use FastAPIOrchestrator from django_fastapi module.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import TYPE_CHECKING

from django_cfg.modules.django_codegen.config import ORM, ORMGenerator, ORMTarget

if TYPE_CHECKING:
    from django_cfg.modules.django_codegen.runner.logger import GenerationLogger


def run_orm(
    cfg: ORM,
    dry_run: bool,
    logger: GenerationLogger,
) -> None:
    """
    Run ORM model generation.

    Converts Django models to:
    - FastAPI: SQLModel models with async CRUD repositories
    - Pydantic: Pure Pydantic schemas
    - SQLAlchemy: SQLAlchemy models (not yet implemented)
    """
    if not cfg.targets:
        return

    logger.gen_start("ORM Generation")

    for target in cfg.targets:
        generator_name = target.generator.value if isinstance(target.generator, ORMGenerator) else target.generator
        apps_str = ", ".join(target.apps) if target.apps else "(all apps)"
        logger.subheader(f"{apps_str} -> {generator_name}")
        logger.info(f"  Output: {target.output}")

        if dry_run:
            logger.skip("Would generate models")
            continue

        try:
            if target.generator == ORMGenerator.FASTAPI:
                _generate_fastapi(target, cfg, logger)
            elif target.generator == ORMGenerator.PYDANTIC:
                _generate_pydantic(target, cfg, logger)
            elif target.generator == ORMGenerator.SQLALCHEMY:
                _generate_sqlalchemy(target, cfg, logger)
            else:
                logger.error(f"Unknown generator: {target.generator}")
        except Exception as e:
            import traceback
            traceback.print_exc()
            logger.error(f"Generation failed: {e}")


def _clean_directory(path: Path, exclude: list[str] | None = None) -> int:
    """Clean directory contents, optionally excluding certain items."""
    if not path.exists():
        return 0

    exclude = exclude or []
    removed = 0

    for item in path.iterdir():
        if item.name in exclude:
            continue
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()
        removed += 1

    return removed


def _generate_fastapi(
    target: ORMTarget,
    cfg: ORM,
    logger: GenerationLogger,
) -> None:
    """Generate FastAPI/SQLModel models from Django models."""
    try:
        from django_cfg.modules.django_fastapi.config import FastAPIConfig
        from django_cfg.modules.django_fastapi.core.orchestrator import FastAPIOrchestrator

        output_dir = Path(target.output)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Clean output directory
        removed = _clean_directory(output_dir, exclude=["__pycache__"])
        if removed:
            logger.info(f"  Cleaned {removed} items")

        # Build FastAPIConfig from ORM config
        fastapi_config = FastAPIConfig(
            enabled=True,
            output_dir=str(output_dir) + "/",
            format="sqlmodel",
            include_crud=cfg.include_crud,
            include_schemas=cfg.include_schemas,
            include_relationships=cfg.include_relationships,
            include_database_config=cfg.include_database_config,
            include_alembic=False,
            async_mode=cfg.async_mode,
            apps=target.apps or [],
            exclude_apps=cfg.exclude_apps,
            use_jsonb=cfg.use_jsonb,
            use_array_fields=cfg.use_array_fields,
            database_env_var=cfg.database_env_var,
            database_default_url=cfg.database_default_url,
        )

        # Create orchestrator and generate
        orchestrator = FastAPIOrchestrator(config=fastapi_config, dry_run=False)

        with logger.spinner("Generating SQLModel models..."):
            result = orchestrator.generate(apps=target.apps or None)

        if result.errors:
            for error in result.errors:
                logger.error(f"  {error}")

        for warning in result.warnings:
            logger.warning(f"  {warning}")

        logger.success(f"Generated {result.files_count} files for {result.models_count} models")
        logger.stats.groups_generated += 1

    except ImportError as e:
        logger.warning(f"django_fastapi module not available: {e}")
        logger.info("  Install: pip install django-cfg[fastapi]")


def _generate_pydantic(
    target: ORMTarget,
    cfg: ORM,
    logger: GenerationLogger,
) -> None:
    """Generate pure Pydantic models from Django models."""
    try:
        from django_cfg.modules.django_fastapi.config import FastAPIConfig
        from django_cfg.modules.django_fastapi.core.orchestrator import FastAPIOrchestrator

        output_dir = Path(target.output)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Clean output directory
        _clean_directory(output_dir, exclude=["__pycache__"])

        # Use pydantic format
        fastapi_config = FastAPIConfig(
            enabled=True,
            output_dir=str(output_dir) + "/",
            format="pydantic",
            include_crud=False,
            include_schemas=True,
            include_relationships=False,
            include_database_config=False,
            include_alembic=False,
            apps=target.apps or [],
            exclude_apps=cfg.exclude_apps,
        )

        orchestrator = FastAPIOrchestrator(config=fastapi_config, dry_run=False)

        with logger.spinner("Generating Pydantic models..."):
            result = orchestrator.generate(apps=target.apps or None)

        logger.success(f"Generated {result.files_count} files for {result.models_count} models")
        logger.stats.groups_generated += 1

    except ImportError as e:
        logger.warning(f"django_fastapi module not available: {e}")


def _generate_sqlalchemy(
    target: ORMTarget,
    cfg: ORM,
    logger: GenerationLogger,
) -> None:
    """Generate SQLAlchemy models from Django models."""
    logger.warning("SQLAlchemy generator not yet implemented")
