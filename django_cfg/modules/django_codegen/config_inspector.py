"""
Config inspection utilities.

Provides typed summaries of generation config for display and debugging.
"""

from pydantic import BaseModel, ConfigDict

from django_cfg.modules.django_codegen.config import Config, TargetType


class TargetSummary(BaseModel):
    """Summary of a single generation target."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    lang: str
    type: str
    path: str
    groups: list[str]
    post_build: str | None = None


class ExtensionsSummary(BaseModel):
    """Summary of auto-discovered extensions."""

    source_path: str
    targets: list[TargetSummary]


class SDKPackageSummary(BaseModel):
    """Summary of an SDK package."""

    name: str
    platform: str
    target: str
    groups: list[str]


class ORMTargetSummary(BaseModel):
    """Summary of an ORM generation target."""

    generator: str
    output: str
    apps: list[str]  # empty = all apps


class ConfigSummary(BaseModel):
    """Typed summary of the full generation config."""

    openapi: list[TargetSummary] = []
    extensions: ExtensionsSummary | None = None
    centrifugo: list[TargetSummary] = []
    sdk: list[SDKPackageSummary] = []
    orm: list[ORMTargetSummary] = []


def inspect_config(config: Config) -> ConfigSummary:
    """Build a typed summary of the generation config."""

    def _target_type_str(t) -> str:
        return t.value if isinstance(t, TargetType) else str(t)

    openapi_targets: list[TargetSummary] = []
    extensions_summary: ExtensionsSummary | None = None

    if config.openapi:
        for t in config.openapi.targets:
            openapi_targets.append(TargetSummary(
                lang=t.lang.value,
                type=_target_type_str(t.type),
                path=str(t.path),
                groups=t.groups,
                post_build=t.post_build,
            ))

        if config.openapi.extensions:
            ext = config.openapi.extensions
            discovered = ext.discover()
            extensions_summary = ExtensionsSummary(
                source_path=str(ext.frontend_path),
                targets=[
                    TargetSummary(
                        lang=t.lang.value,
                        type=_target_type_str(t.type),
                        path=str(t.path),
                        groups=t.groups,
                        post_build=t.post_build,
                    )
                    for t in discovered
                ],
            )

    centrifugo_targets: list[TargetSummary] = []
    if config.centrifugo:
        for t in config.centrifugo.targets:
            centrifugo_targets.append(TargetSummary(
                lang=t.lang.value,
                type=_target_type_str(t.type),
                path=str(t.path),
                groups=t.groups,
                post_build=t.post_build,
            ))

    sdk_packages: list[SDKPackageSummary] = []
    if config.sdk:
        for pkg in config.sdk.packages:
            sdk_packages.append(SDKPackageSummary(
                name=pkg.name,
                platform=pkg.platform.value,
                target=str(pkg.target),
                groups=pkg.groups,
            ))

    orm_targets: list[ORMTargetSummary] = []
    if config.orm:
        for t in config.orm.targets:
            gen = t.generator.value if hasattr(t.generator, "value") else str(t.generator)
            orm_targets.append(ORMTargetSummary(
                generator=gen,
                output=str(t.output),
                apps=t.apps,
            ))

    return ConfigSummary(
        openapi=openapi_targets,
        extensions=extensions_summary,
        centrifugo=centrifugo_targets,
        sdk=sdk_packages,
        orm=orm_targets,
    )
