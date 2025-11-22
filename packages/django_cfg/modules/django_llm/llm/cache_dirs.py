"""
Cache Directory Builder for Django LLM.

Centralized cache directory management with smart defaults.
"""
from pathlib import Path
from typing import Optional


class CacheDirectoryBuilder:
    """Builder for cache directories with smart defaults."""

    DEFAULT_CACHE_ROOT = ".cache"
    DEFAULT_DJANGO_LLM_DIR = "django_llm"

    def __init__(self):
        self._cache_root: Optional[Path] = None
        self._subdir: Optional[str] = None
        self._base_path: Optional[Path] = None

    def with_cache_root(self, root: str = DEFAULT_CACHE_ROOT) -> "CacheDirectoryBuilder":
        """Set cache root directory (default: .cache)."""
        self._cache_root = Path(root)
        return self

    def with_subdir(self, subdir: str) -> "CacheDirectoryBuilder":
        """Set subdirectory within cache root."""
        self._subdir = subdir
        return self

    def with_base_path(self, path: Path) -> "CacheDirectoryBuilder":
        """Set base path (default: cwd)."""
        self._base_path = path
        return self

    def from_django_settings(self) -> "CacheDirectoryBuilder":
        """Try to use Django cache location if available."""
        try:
            from django.conf import settings
            if hasattr(settings, 'CACHES') and 'default' in settings.CACHES:
                cache_location = settings.CACHES['default'].get('LOCATION')
                # Only use cache_location if it's a file path, not a Redis URL
                if cache_location and not cache_location.startswith(('redis://', 'rediss://')):
                    self._base_path = Path(cache_location).parent
                    self._cache_root = Path(cache_location).name
        except:
            pass
        return self

    def build(self) -> Path:
        """Build the cache directory path."""
        # Base path
        base = self._base_path or Path.cwd()

        # Cache root
        cache_root = self._cache_root or Path(self.DEFAULT_CACHE_ROOT)

        # Build path
        if self._subdir:
            cache_dir = base / cache_root / self._subdir
        else:
            cache_dir = base / cache_root

        # Ensure directory exists
        cache_dir.mkdir(parents=True, exist_ok=True)

        return cache_dir


def get_default_llm_cache_dir(cache_dir: Optional[Path] = None) -> Path:
    """
    Get default LLM cache directory with smart fallbacks.

    Priority:
    1. Provided cache_dir
    2. Django CACHES setting (if file-based)
    3. .cache/django_llm in current directory

    Args:
        cache_dir: Optional cache directory override

    Returns:
        Path to cache directory (created if doesn't exist)
    """
    if cache_dir:
        # Use provided directory
        cache_path = Path(cache_dir)
        cache_path.mkdir(parents=True, exist_ok=True)
        return cache_path

    # Build with smart defaults
    return (
        CacheDirectoryBuilder()
        .from_django_settings()
        .with_cache_root(".cache")
        .with_subdir("django_llm")
        .build()
    )


def get_models_cache_dir(cache_dir: Optional[Path] = None) -> Path:
    """Get models cache directory."""
    return get_default_llm_cache_dir(cache_dir)


def get_translator_cache_dir(cache_dir: Optional[Path] = None) -> Path:
    """Get translator cache directory."""
    if cache_dir:
        cache_path = Path(cache_dir)
        cache_path.mkdir(parents=True, exist_ok=True)
        return cache_path

    return (
        CacheDirectoryBuilder()
        .from_django_settings()
        .with_cache_root(".cache")
        .with_subdir("translations")
        .build()
    )
