"""OpenAPI generation runner — bridges user Config → pipeline.

Reads `OpenAPI(targets=[Target(...)])` from generation.py, translates each
Target into a pipeline GenerationTarget, and dispatches via
`openapi/pipeline/runner.run_pipeline()` (drf-spectacular → tag-slice →
external CLI: ogen / Hey API / openapi-python-client / swift-openapi).

The legacy `call_command("generate_clients")` path was removed; in-house
emitters now live under `django_generator/@archive/django_client_old/`
and are not on the import path. The pipeline writes directly to each
Target.path — no copy_groups / wildcard expansion needed.
"""

from __future__ import annotations

from pathlib import Path

from ..pipeline.config import (
    GenerationTarget,
    OpenAPIConfig,
)
from ..pipeline.runner import run_pipeline
from ..service import get_openapi_service
from .logger import GenerationLogger
from .utils import (
    fix_go_imports,
    run_post_build,
)
from ...public.config import OpenAPI

_LANG_DEFAULT_TOOL: dict[str, str] = {
    "typescript": "hey-api",
    "python": "openapi-python-client",
    "go": "ogen",
    "swift": "swift-openapi",
    "swift_codable": "swift-openapi",
    "proto": "buf",
}


def run_openapi(
    cfg: OpenAPI,
    only_platforms: list[str] | None,
    only_target: str | None,
    only_groups: list[str] | None,
    dry_run: bool,
    logger: GenerationLogger,
) -> None:
    """Translate user Targets to pipeline GenerationTargets and run."""
    targets = _build_targets(cfg, only_platforms, only_target, only_groups)
    if not targets:
        logger.warning("No targets to run")
        return

    if dry_run:
        for t in targets:
            logger.skip(f"Would generate {t.name} → {t.path}")
        return

    service = get_openapi_service()
    if not service.is_enabled():
        # Project hasn't configured django-cfg openapi_client — fall back
        # to a permissive default so the pipeline runs against live DRF.
        service.set_config(OpenAPIConfig(enabled=True))

    logger.gen_start("OpenAPI", "all platforms")
    report = run_pipeline(service.config, targets, dry_run=False)

    for name in report.targets_run:
        logger.success(f"✓ {name}")
    for name, err in report.failures:
        logger.error(f"✗ {name}: {err}")

    if not report.ok:
        return

    # Per-Target post-processing: Go imports rewrite + post_build hook.
    for t in cfg.targets:
        if not t.matches_filter(only_target):
            continue
        lang = t.lang.value if hasattr(t.lang, "value") else str(t.lang)
        if only_platforms and lang not in only_platforms:
            continue
        if lang == "go" and cfg.go_module:
            fix_go_imports(Path(t.path), cfg.go_module, logger)
        if t.post_build:
            run_post_build(Path(t.path), t.post_build, logger)


def _build_targets(
    cfg: OpenAPI,
    only_platforms: list[str] | None,
    only_target: str | None,
    only_groups: list[str] | None,
) -> list[GenerationTarget]:
    plat_filter = set(only_platforms or [])
    group_filter = set(only_groups or [])

    user_targets = list(cfg.targets)
    if cfg.extensions is not None:
        user_targets.extend(cfg.extensions.discover())

    out: list[GenerationTarget] = []
    for i, t in enumerate(user_targets):
        if not t.matches_filter(only_target):
            continue
        lang = t.lang.value if hasattr(t.lang, "value") else str(t.lang)
        if plat_filter and lang not in plat_filter:
            continue
        tool = _LANG_DEFAULT_TOOL.get(lang)
        if tool is None:
            continue

        groups = list(t.groups)
        if group_filter:
            groups = [g for g in groups if g in group_filter or "*" in g]
            if not groups:
                continue

        type_str = t.type.value if hasattr(t.type, "value") else str(t.type)
        name = f"{lang}-{type_str}-{i}"
        source_path: Path | None = None
        if cfg.source_root is not None:
            source_path = Path(cfg.source_root) / name
        out.append(
            GenerationTarget(
                name=name,
                lang=lang,  # type: ignore[arg-type]
                tool=tool,  # type: ignore[arg-type]
                path=Path(t.path),
                groups=groups,
                options={},
                source_path=source_path,
            )
        )
    return out


__all__ = ["run_openapi"]
