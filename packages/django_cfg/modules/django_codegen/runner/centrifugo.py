"""
Centrifugo generation runner.

v6.1: Rich logging integration.
v6.2: Platform enum instead of Language.
v6.3: New targets format (list[Target]).
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import TYPE_CHECKING

from django.conf import settings
from django.core.management import call_command

from django_cfg.modules.django_codegen.config import Centrifugo

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
    # Group targets by platform
    by_platform: dict[str, list] = {}
    for target in cfg.targets:
        key = target.lang.value
        by_platform.setdefault(key, []).append(target)

    for platform, targets in by_platform.items():
        if only_platforms and platform not in only_platforms:
            continue

        all_groups = [g for t in targets for g in t.groups]
        effective_groups = all_groups
        if only_groups:
            effective_groups = [g for g in all_groups if g in only_groups]

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

        # Copy entire generated dir to each target path (centrifugo has no per-group subfolders)
        source = Path(settings.BASE_DIR) / "openapi" / "centrifuge" / platform
        for target in targets:
            if not source.exists():
                logger.warning(f"Source not found: {source}")
                continue
            target.path.mkdir(parents=True, exist_ok=True)
            if target.path.exists():
                shutil.rmtree(target.path)
            shutil.copytree(source, target.path)
            logger.gen_complete(1)
