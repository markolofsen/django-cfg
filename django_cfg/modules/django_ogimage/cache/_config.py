from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings


class OGImageConfig(BaseSettings):
    """Configuration for django_ogimage module.

    Environment overrides:
        OGIMAGE__MEDIA_SUBDIR  — subdirectory inside MEDIA_ROOT (default: ogimage)
        OGIMAGE__CACHE_ENABLED — set to false to always re-render (default: true)
    """

    media_subdir: str = "ogimage"
    cache_enabled: bool = True

    model_config = {"env_prefix": "OGIMAGE__", "populate_by_name": True}

    def cache_dir(self) -> Path:
        from django_cfg.core.utils.paths import get_media_path
        return get_media_path(self.media_subdir)


@lru_cache(maxsize=1)
def get_og_config() -> OGImageConfig:
    return OGImageConfig()
