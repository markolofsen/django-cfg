"""
OpenAPI generation runner.

v6.1: Rich logging integration.
v6.2: Platform enum instead of Language.
"""

from django.core.management import call_command

from django_cfg.modules.django_codegen.config import Platform, OpenAPI
from django_cfg.modules.django_codegen.runner.logger import GenerationLogger
from django_cfg.modules.django_codegen.runner.utils import (
    copy_groups,
    expand_wildcards,
    fix_go_imports,
    get_source_dir,
    run_post_build,
)


def run_openapi(
    cfg: OpenAPI,
    only_platforms: list[str] | None,
    only_target: str | None,
    only_groups: list[str] | None,
    dry_run: bool,
    logger: GenerationLogger,
) -> None:
    """Run OpenAPI generation."""
    # Handle both legacy and new format
    if cfg.is_legacy_format():
        _run_openapi_legacy(cfg, only_platforms, only_groups, dry_run, logger)
    else:
        _run_openapi_new(cfg, only_platforms, only_target, only_groups, dry_run, logger)


def _run_openapi_legacy(
    cfg: OpenAPI,
    only_platforms: list[str] | None,
    only_groups: list[str] | None,
    dry_run: bool,
    logger: GenerationLogger,
) -> None:
    """Run OpenAPI generation with legacy config format."""
    platforms = {
        "typescript": cfg.typescript,
        "python": cfg.python,
        "go": cfg.go,
        "swift": cfg.swift,
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

        logger.gen_start("OpenAPI", platform)
        logger.gen_groups(effective_groups)

        if dry_run:
            logger.skip(f"Would generate and copy {len(effective_groups)} groups")
            continue

        # Generate
        try:
            cmd_opts: dict = {
                platform: True,
                "groups": effective_groups,
            }
            # Disable other platforms (only typescript, python, go have no_ flags)
            for other in ["typescript", "python", "go"]:
                if other != platform:
                    cmd_opts[f"no_{other}"] = True

            with logger.spinner(f"Generating {platform}..."):
                call_command("generate_clients", **cmd_opts)
            logger.success(f"Generated {len(effective_groups)} groups")
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            continue

        # Copy
        if platform in cfg.legacy_targets:
            target = cfg.legacy_targets[platform]
            source = get_source_dir(platform)

            copied = copy_groups(source, target, effective_groups, logger)
            logger.gen_complete(copied)

            # Go import fixing
            if platform == "go" and cfg.go_module:
                fix_go_imports(target, cfg.go_module, logger)


def _run_openapi_new(
    cfg: OpenAPI,
    only_platforms: list[str] | None,
    only_target: str | None,
    only_groups: list[str] | None,
    dry_run: bool,
    logger: GenerationLogger,
) -> None:
    """Run OpenAPI generation with new list-based config format.

    Flow:
    1. Collect explicit groups (no wildcards) for generate_clients
    2. Generate all requested groups
    3. After generation, expand wildcards by scanning source directory
    4. Copy expanded groups to targets
    """
    for platform in Platform:
        if only_platforms and platform.value not in only_platforms:
            continue

        # Get all targets for this platform (including auto-discovered)
        all_targets = cfg.get_targets_for_lang(platform)

        # Filter by target type
        targets = [t for t in all_targets if t.matches_filter(only_target)]

        if not targets:
            continue

        # Collect all groups needed for generation
        # Split into explicit groups and wildcard patterns
        all_groups: set[str] = set()
        wildcard_patterns: set[str] = set()

        for target in targets:
            for group in target.groups:
                if "*" in group:
                    wildcard_patterns.add(group)
                else:
                    all_groups.add(group)

        # Apply group filter to explicit groups
        if only_groups:
            all_groups = all_groups.intersection(only_groups)

        # For generation: use explicit groups only
        # Wildcards will be resolved after generation by scanning source dir
        groups_for_generation = list(all_groups)

        logger.gen_start("OpenAPI", platform.value)
        logger.gen_groups(list(all_groups), "Explicit groups")
        if wildcard_patterns:
            logger.gen_wildcards(list(wildcard_patterns))

        if dry_run:
            for target in targets:
                logger.skip(f"Would generate and copy to {target.path}")
            continue

        # Generate groups
        # If wildcards present - generate ALL groups (so wildcards can match)
        # Otherwise - generate only explicit groups
        try:
            cmd_opts: dict = {
                platform.value: True,
            }
            for other in ["typescript", "python", "go"]:
                if other != platform.value:
                    cmd_opts[f"no_{other}"] = True

            if wildcard_patterns:
                # Wildcards present - generate all (no groups filter)
                with logger.spinner(f"Generating all {platform.value} groups (wildcards)..."):
                    call_command("generate_clients", **cmd_opts)
                logger.success("Generated all groups (wildcards will be matched)")
            elif groups_for_generation:
                # Only explicit groups
                cmd_opts["groups"] = groups_for_generation
                with logger.spinner(f"Generating {len(groups_for_generation)} {platform.value} groups..."):
                    call_command("generate_clients", **cmd_opts)
                logger.success(f"Generated {len(groups_for_generation)} explicit groups")
            else:
                logger.warning("No groups to generate")
                continue
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            continue

        # Now expand wildcards - source directory should exist
        source = get_source_dir(platform)

        # Copy to each target
        for target in targets:
            target_groups = target.groups
            if only_groups:
                target_groups = [g for g in target_groups if g in only_groups or "*" in g]

            # Expand wildcards NOW (after generation)
            expanded_target_groups = expand_wildcards(target_groups, platform)

            if not expanded_target_groups:
                logger.warning(f"No matching groups for {target.path}")
                continue

            target_type_str = target.type.value if hasattr(target.type, "value") else str(target.type)
            logger.gen_target(target_type_str, target.path, platform.value)
            copied = copy_groups(source, target.path, expanded_target_groups, logger)
            logger.gen_complete(copied, f"groups to {target.path.name}")

            # Go import fixing
            if platform == Platform.GO and cfg.go_module:
                fix_go_imports(target.path, cfg.go_module, logger)

            # Post-build hook
            if target.post_build:
                run_post_build(target.path, target.post_build, logger)
