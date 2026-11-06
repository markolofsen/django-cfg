"""
Cache directories for the LLM module.

Everything resolves through ``django_cfg.core.utils.runtime_paths``: explicit
argument, config ``cache_dir``, ``DJANGO_CFG_CACHE_DIR``, then the per-user
cache dir of the project. Directories are created on first use, with a
fallback to the temp dir (one warning) when the target is not writable.
"""
from pathlib import Path
from typing import Optional

from django_cfg.core.utils import runtime_paths as rp

#: Deprecated alias; it named the LLM cache dir itself. Use DJANGO_CFG_CACHE_DIR (the root).
CACHE_DIR_ENV = rp.LEGACY_ENV_LLM_CACHE_DIR

DJANGO_LLM_DIR = "django_cfg.modules.django_llm"


class CacheDirectoryBuilder:
    """Thin compatibility builder; resolves through the shared runtime-paths resolver."""

    DEFAULT_DJANGO_LLM_DIR = DJANGO_LLM_DIR

    def __init__(self):
        self._subdir: Optional[str] = None
        self._base_path: Optional[Path] = None

    def with_cache_root(self, root: str = ".cache") -> "CacheDirectoryBuilder":
        """No-op: the cache root comes from DJANGO_CFG_CACHE_DIR / config ``cache_dir``."""
        return self

    def with_subdir(self, subdir: str) -> "CacheDirectoryBuilder":
        self._subdir = subdir
        return self

    def with_base_path(self, path: Path) -> "CacheDirectoryBuilder":
        """Use ``path`` as the cache root."""
        self._base_path = path
        return self

    def from_django_settings(self) -> "CacheDirectoryBuilder":
        return self

    def build(self) -> Path:
        parts = (self._subdir,) if self._subdir else ()
        return rp.ensure_dir(rp.resolve_cache_dir(*parts, explicit=self._base_path))


def get_default_llm_cache_dir(cache_dir: Optional[Path] = None) -> Path:
    """
    LLM cache directory (models catalogue, ``llm/`` responses, ``images/``).

    Priority: ``cache_dir`` argument, deprecated ``CMDOP_LLM_CACHE_DIR`` (used as-is),
    then ``<cache root>/django_cfg.modules.django_llm``.
    """
    if cache_dir:
        return rp.ensure_dir(Path(cache_dir))
    import os

    legacy = os.environ.get(CACHE_DIR_ENV)
    if legacy:
        rp.warn_deprecated_env()
        return rp.ensure_dir(Path(legacy))
    return rp.ensure_dir(rp.resolve_cache_dir(DJANGO_LLM_DIR))


def get_models_cache_dir(cache_dir: Optional[Path] = None) -> Path:
    """Get models cache directory."""
    return get_default_llm_cache_dir(cache_dir)


def get_images_cache_dir(cache_dir: Optional[Path] = None) -> Path:
    """Vision image cache directory (shared LLM cache dir + ``images``)."""
    if cache_dir:
        return rp.ensure_dir(Path(cache_dir))
    return rp.ensure_dir(get_default_llm_cache_dir() / "images")


def get_translator_cache_dir(cache_dir: Optional[Path] = None) -> Path:
    """Get translator cache directory."""
    if cache_dir:
        return rp.ensure_dir(Path(cache_dir))
    return rp.ensure_dir(rp.resolve_cache_dir("translations"))
