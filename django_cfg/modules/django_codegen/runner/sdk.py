"""
SDK generation runner.

v6.1: Rich logging integration.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.core.management import call_command

from django_cfg.modules.django_codegen.config import SDK
from django_cfg.modules.django_codegen.runner.utils import copy_groups, get_source_dir

if TYPE_CHECKING:
    from django_cfg.modules.django_codegen.runner.logger import GenerationLogger


def run_sdk(
    cfg: SDK,
    only_groups: list[str] | None,
    dry_run: bool,
    logger: GenerationLogger,
) -> None:
    """Run SDK package generation."""
    for pkg in cfg.packages:
        effective_groups = pkg.groups
        if only_groups:
            effective_groups = [g for g in pkg.groups if g in only_groups]

        if not effective_groups:
            continue

        logger.gen_start(f"SDK {pkg.name}", pkg.platform.value)
        logger.gen_groups(effective_groups)

        if dry_run:
            logger.skip(f"Would generate and copy {len(effective_groups)} groups")
            continue

        # Generate
        platform = pkg.platform.value
        try:
            cmd_opts: dict = {
                platform: True,
                "groups": effective_groups,
            }
            for other in ["typescript", "python", "go"]:
                if other != platform:
                    cmd_opts[f"no_{other}"] = True

            with logger.spinner(f"Generating SDK {pkg.name}..."):
                call_command("generate_clients", **cmd_opts)
            logger.success(f"Generated {len(effective_groups)} groups")
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            continue

        # Copy
        source = get_source_dir(platform)
        copied = copy_groups(source, pkg.target, effective_groups, logger)
        logger.gen_complete(copied, f"groups to {pkg.target.name}")
