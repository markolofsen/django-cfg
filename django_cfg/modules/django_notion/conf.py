"""Access to ``DjangoConfig.notion``. One indirection so tests can swap the config."""

from __future__ import annotations

from .__cfg__ import NotionConfig
from .exceptions import NotionConfigError


def get_notion_config() -> NotionConfig:
    from django_cfg.core.state import get_current_config

    config = get_current_config()
    notion = getattr(config, "notion", None) if config else None
    if notion is None or not notion.enabled:
        raise NotionConfigError("django_notion is not enabled: set DjangoConfig.notion = NotionConfig(enabled=True, ...)")
    return notion


def project_name(cfg: NotionConfig) -> str:
    if cfg.project:
        return cfg.project
    from django_cfg.core.state import get_current_config

    config = get_current_config()
    return (getattr(config, "project_name", "") or "django").strip().lower().replace(" ", "-")
