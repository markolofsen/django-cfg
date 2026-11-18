"""
ORM/FastAPI model generation runner.

Generates Pydantic/FastAPI models from Django ORM models.

v6.1: Rich logging integration.
v6.2: Use FastAPIOrchestrator from django_generator.fastapi.

The output folder is never cleaned in place: a target is generated into a
staged copy next to it and swapped in only when generation succeeded and git
shows no uncommitted work under it (``pipeline/staging.py``). Target apps are
checked against the app registry before anything is written
(``validate_orm``).
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import TYPE_CHECKING

from ...public.config import ORM, ORMGenerator, ORMTarget
from ..pipeline.errors import GeneratorError
from ..pipeline.staging import Stage

if TYPE_CHECKING:
    from .logger import GenerationLogger


class ORMGenerationError(Exception):
    """The generator reported errors or produced nothing; the output is left as it was."""


def validate_orm(cfg: ORM) -> list[str]:
    """Problems that would make an ORM target fail, found before anything is written.

    An app in ``ORMTarget.apps`` must be an installed app label (``apps.get_app_config``
    is what the parser calls). Returns one message per problem; empty when fine.
    """
    from difflib import get_close_matches

    from django.apps import apps as registry

    known = sorted(c.label for c in registry.get_app_configs())
    problems: list[str] = []
    for target in cfg.targets:
        for label in target.apps:
            if label in cfg.exclude_apps or label in known:
                continue
            hint = get_close_matches(label, known, n=3)
            problems.append(
                f"ORM target {target.output}: app '{label}' is not installed"
                + (f" (did you mean: {', '.join(hint)}?)" if hint else "")
                + ". Remove it from ORMTarget.apps; nothing was written."
            )
    return problems


def run_orm(
    cfg: ORM,
    dry_run: bool,
    logger: GenerationLogger,
    *,
    force: bool = False,
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

    problems = validate_orm(cfg)
    if problems:
        for problem in problems:
            logger.error(problem)
        return

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
                _generate(target, cfg, logger, fmt="sqlmodel", force=force)
            elif target.generator == ORMGenerator.PYDANTIC:
                _generate(target, cfg, logger, fmt="pydantic", force=force)
            elif target.generator == ORMGenerator.SQLALCHEMY:
                _generate_sqlalchemy(target, cfg, logger)
            else:
                logger.error(f"Unknown generator: {target.generator}")
        except (ORMGenerationError, GeneratorError) as e:
            logger.error(f"Generation failed, {target.output} left as it was: {e}")
        except Exception as e:
            import traceback
            traceback.print_exc()
            logger.error(f"Generation failed, {target.output} left as it was: {e}")


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


def _check_result(result) -> None:
    """Turn a failed or empty generation into an exception, before the swap."""
    if result.errors:
        raise ORMGenerationError("; ".join(result.errors))
    if not result.files:
        reason = "; ".join(result.warnings) or "no models found"
        raise ORMGenerationError(f"generated no files ({reason})")


def _fastapi_config(output_dir: Path, target: ORMTarget, cfg: ORM, fmt: str):
    from ...fastapi.config import FastAPIConfig

    common = dict(
        enabled=True,
        output_dir=str(output_dir) + "/",
        format=fmt,
        include_alembic=False,
        apps=target.apps or [],
        exclude_apps=cfg.exclude_apps,
    )
    if fmt == "pydantic":
        return FastAPIConfig(
            **common,
            include_crud=False,
            include_schemas=True,
            include_relationships=False,
            include_database_config=False,
        )
    return FastAPIConfig(
        **common,
        include_crud=cfg.include_crud,
        include_schemas=cfg.include_schemas,
        include_relationships=cfg.include_relationships,
        include_database_config=cfg.include_database_config,
        async_mode=cfg.async_mode,
        use_jsonb=cfg.use_jsonb,
        use_array_fields=cfg.use_array_fields,
        database_env_var=cfg.database_env_var,
        database_default_url=cfg.database_default_url,
    )


def _generate(
    target: ORMTarget,
    cfg: ORM,
    logger: GenerationLogger,
    *,
    fmt: str,
    force: bool = False,
) -> None:
    """Generate SQLModel (``sqlmodel``) or pure Pydantic (``pydantic``) models.

    Cleans and writes a staged copy of ``target.output``; the real folder is
    replaced only after the orchestrator reported no errors and produced files,
    and after the git guard (``Stage.commit``).
    """
    try:
        from ...fastapi.core.orchestrator import FastAPIOrchestrator
    except ImportError as e:
        logger.warning(f"django_generator.fastapi not available: {e}")
        logger.info("  Install: pip install django-cfg[fastapi]")
        return

    stage = Stage.open(Path(target.output))
    try:
        removed = _clean_directory(stage.path, exclude=["__pycache__"])
        if removed:
            logger.info(f"  Cleaned {removed} items (in the staged copy)")
        orchestrator = FastAPIOrchestrator(
            config=_fastapi_config(stage.path, target, cfg, fmt), dry_run=False
        )
        label = "SQLModel" if fmt == "sqlmodel" else "Pydantic"
        with logger.spinner(f"Generating {label} models..."):
            result = orchestrator.generate(apps=target.apps or None)
        _check_result(result)
        stage.commit(force=force)
    except BaseException:
        stage.discard()
        raise

    for warning in result.warnings:
        logger.warning(f"  {warning}")
    logger.success(f"Generated {result.files_count} files for {result.models_count} models")
    logger.stats.groups_generated += 1


def _generate_sqlalchemy(
    target: ORMTarget,
    cfg: ORM,
    logger: GenerationLogger,
) -> None:
    """Generate SQLAlchemy models from Django models."""
    logger.warning("SQLAlchemy generator not yet implemented")
