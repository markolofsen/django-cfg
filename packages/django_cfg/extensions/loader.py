"""
Extension Loader

Loads discovered extensions and integrates them with Django.
"""

import warnings
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional

from django_cfg.utils import get_logger

from .scanner import DiscoveredExtension, ExtensionScanner

if TYPE_CHECKING:
    from django.urls import URLPattern, URLResolver

logger = get_logger(__name__)

# Global loader instance
_loader: Optional["ExtensionLoader"] = None


class ExtensionLoader:
    """
    Loads and integrates discovered extensions with Django.

    Handles:
    - Adding extensions to INSTALLED_APPS
    - Collecting URL patterns
    - Collecting middleware from extensions
    - Version compatibility checks
    - Logging extension status

    Usage:
        loader = ExtensionLoader(base_path=Path("/path/to/project"))

        # Get apps for INSTALLED_APPS
        apps = loader.get_installed_apps()

        # Get URL patterns
        urlpatterns = loader.get_urlpatterns()

        # Get middleware from extensions
        middleware = loader.get_middleware()
    """

    def __init__(
        self,
        base_path: Optional[Path] = None,
        scanner: Optional[ExtensionScanner] = None,
    ):
        """
        Initialize loader.

        Args:
            base_path: Project root path.
            scanner: Optional pre-configured scanner.
        """
        self.scanner = scanner or ExtensionScanner(base_path=base_path)
        self._installed_apps_cache: Optional[List[str]] = None
        self._middleware_cache: Optional[List[str]] = None
        self._version_checked: set = set()

    def get_installed_apps(self) -> List[str]:
        """
        Get list of Django app paths for INSTALLED_APPS.

        Only returns valid app extensions (not modules).

        Returns:
            List of app paths like ['extensions.apps.leads', 'extensions.apps.support']
        """
        if self._installed_apps_cache is not None:
            return self._installed_apps_cache

        apps: List[str] = []

        for ext in self.scanner.discover_apps():
            if not ext.is_valid:
                logger.warning(
                    f"Skipping invalid extension '{ext.name}': {ext.errors}"
                )
                continue

            # Check version compatibility
            self._check_version_compatibility(ext)

            # Build app path
            app_path = f"extensions.apps.{ext.name}"
            apps.append(app_path)
            logger.info(f"Loaded extension: {ext.name} v{ext.manifest.version if ext.manifest else '?'}")

        self._installed_apps_cache = apps
        return apps

    def get_urlpatterns(self) -> List["URLPattern | URLResolver"]:
        """
        Get URL patterns for all extensions with url_prefix.

        Returns:
            List of URL patterns to include in project urls.py
        """
        from django.urls import include, path

        patterns: List = []

        for ext in self.scanner.discover_apps():
            if not ext.is_valid or not ext.manifest:
                continue

            if not ext.manifest.url_prefix:
                continue

            # Try to import extension's urls
            try:
                urls_module = f"extensions.apps.{ext.name}.urls"
                namespace = ext.manifest.get_url_namespace()

                patterns.append(
                    path(
                        f"{ext.manifest.url_prefix}/",
                        include(urls_module, namespace=namespace),
                    )
                )
                logger.debug(f"Added URL pattern for {ext.name}: /{ext.manifest.url_prefix}/")
            except ImportError:
                logger.debug(f"Extension {ext.name} has no urls.py")
            except Exception as e:
                logger.warning(f"Failed to load URLs for {ext.name}: {e}")

        return patterns

    def get_middleware(self) -> List[str]:
        """
        Get middleware classes from all extensions.

        Collects middleware from extensions that define middleware_classes
        or override get_middleware_classes().

        Returns:
            List of middleware class paths
        """
        if self._middleware_cache is not None:
            return self._middleware_cache

        middleware: List[str] = []

        for ext in self.scanner.discover_apps():
            if not ext.is_valid:
                continue

            # Try to load extension settings and get middleware
            try:
                cfg_module = __import__(
                    f"extensions.apps.{ext.name}.__cfg__",
                    fromlist=["settings"]
                )
                if hasattr(cfg_module, "settings"):
                    settings = cfg_module.settings
                    if hasattr(settings, "get_middleware_classes"):
                        ext_middleware = settings.get_middleware_classes()
                        middleware.extend(ext_middleware)
                        if ext_middleware:
                            logger.debug(f"Extension {ext.name} middleware: {ext_middleware}")
            except ImportError:
                logger.debug(f"Extension {ext.name} has no __cfg__.py")
            except Exception as e:
                logger.warning(f"Failed to load middleware for {ext.name}: {e}")

        self._middleware_cache = middleware
        return middleware

    def get_extension_info(self) -> List[dict]:
        """
        Get information about all discovered extensions.

        Returns:
            List of dicts with extension info for debugging/admin.
        """
        info = []
        for ext in self.scanner.discover_all():
            info.append({
                "name": ext.name,
                "type": ext.type,
                "version": ext.manifest.version if ext.manifest else None,
                "is_valid": ext.is_valid,
                "errors": ext.errors,
                "path": str(ext.path),
                "description": ext.manifest.description if ext.manifest else None,
            })
        return info

    def print_status(self) -> None:
        """Print extension status to console."""
        extensions = self.scanner.discover_all()

        if not extensions:
            print("No extensions found in extensions/ folder")
            return

        print(f"\nDiscovered {len(extensions)} extension(s):\n")

        for ext in extensions:
            status = "✓" if ext.is_valid else "✗"
            version = f"v{ext.manifest.version}" if ext.manifest else "no manifest"
            ext_type = f"[{ext.type}]"

            print(f"  {status} {ext.name} {ext_type} - {version}")

            if ext.errors:
                for error in ext.errors:
                    print(f"      └── {error}")

        print()

    def _check_version_compatibility(self, ext: DiscoveredExtension) -> None:
        """
        Check if django_cfg version is compatible with extension.

        Emits warning if version is too low.
        """
        if ext.name in self._version_checked:
            return

        self._version_checked.add(ext.name)

        if not ext.manifest or not ext.manifest.min_djangocfg_version:
            return

        try:
            from packaging import version as pkg_version
        except ImportError:
            # packaging not available, skip check
            return

        try:
            # Get current django_cfg version
            from django_cfg import __version__

            required = pkg_version.parse(ext.manifest.min_djangocfg_version)
            current = pkg_version.parse(__version__)

            if current < required:
                warnings.warn(
                    f"Extension '{ext.name}' v{ext.manifest.version} "
                    f"requires django_cfg >= {ext.manifest.min_djangocfg_version}, "
                    f"but you have {__version__}. Some features may not work.",
                    UserWarning,
                    stacklevel=2,
                )
        except Exception as e:
            logger.debug(f"Version check failed for {ext.name}: {e}")

    def clear_cache(self) -> None:
        """Clear all caches."""
        self.scanner.clear_cache()
        self._installed_apps_cache = None
        self._middleware_cache = None
        self._version_checked.clear()


def get_extension_loader(base_path: Optional[Path] = None) -> ExtensionLoader:
    """
    Get or create the global ExtensionLoader instance.

    Args:
        base_path: Project root path. Only used on first call.

    Returns:
        Global ExtensionLoader instance.
    """
    global _loader

    if _loader is None:
        _loader = ExtensionLoader(base_path=base_path)

    return _loader


def reset_extension_loader() -> None:
    """Reset the global loader (useful for testing)."""
    global _loader
    _loader = None
