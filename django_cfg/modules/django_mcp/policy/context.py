"""Resolve a URL-selected profile once; never inherit another profile's models."""

from typing import Any

from django_cfg.modules.django_mcp.__cfg__ import AppMCPConfig, DjangoMCPModuleConfig, IntrospectionConfig
from django_cfg.modules.django_mcp.exceptions import MCPPermissionDenied


def effective_context(config: Any, profile: Any) -> tuple[Any, Any]:
    if not isinstance(config, DjangoMCPModuleConfig):
        return config, profile
    if profile is not None:
        selected = config.profiles.get(profile.name)
    else:
        selected = config.profiles.get("default")
        if selected is None and len(config.profiles) == 1:
            selected = next(iter(config.profiles.values()))
    if selected is None:
        raise MCPPermissionDenied("An explicit MCP profile is required.")
    apps: dict[str, AppMCPConfig] = {}
    for qualified, grant in selected.exposures.items():
        app, model = qualified.lower().split(".")
        if app not in apps:
            apps[app] = AppMCPConfig(enabled=True, models={})
        apps[app].models[model] = grant.model_copy(deep=True)
    return config.model_copy(update={
        "exposed_apps": apps,
        "introspection": (selected.introspection or IntrospectionConfig()).model_copy(deep=True),
    }, deep=True), selected
