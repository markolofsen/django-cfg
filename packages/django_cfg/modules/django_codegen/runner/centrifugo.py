"""
Centrifugo generation runner.

v6.1: Rich logging integration.
v6.2: Platform enum instead of Language.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from django.core.management import call_command

from django_cfg.modules.django_codegen.config import Centrifugo
from django_cfg.modules.django_codegen.runner.utils import copy_groups

if TYPE_CHECKING:
    from django_cfg.modules.django_codegen.runner.logger import GenerationLogger


def run_centrifugo(
    cfg: Centrifugo,
    only_platforms: list[str] | None,
    only_groups: list[str] | None,
    dry_run: bool,
    logger: GenerationLogger,
) -> None:
    """Run Centrifugo generation."""
    platforms = {
        "typescript": cfg.typescript,
        "swift": cfg.swift,
        "go": cfg.go,
    }

    for platform, groups in platforms.items():
        if not groups:
            continue
        if only_platforms and platform not in only_platforms:
            continue

        effective_groups = groups
        if only_groups:
            effective_groups = [g for g in groups if g in only_groups]

        if not effective_groups:
            continue

        logger.gen_start("Centrifugo", platform)
        logger.gen_groups(effective_groups)

        if dry_run:
            logger.skip(f"Would generate and copy {len(effective_groups)} groups")
            continue

        # Generate
        try:
            with logger.spinner(f"Generating Centrifugo {platform}..."):
                call_command("generate_centrifugo_clients", **{platform: True})
            logger.success(f"Generated {len(effective_groups)} groups")
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            continue

        # Copy
        if platform in cfg.targets:
            target = cfg.targets[platform]
            from django.conf import settings

            source = Path(settings.BASE_DIR) / "openapi" / "centrifuge" / platform

            copied = copy_groups(source, target, effective_groups, logger)
            logger.gen_complete(copied)
