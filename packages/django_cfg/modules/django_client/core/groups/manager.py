"""
Application Group Manager.

Manages application groups and URL pattern generation.
"""

import importlib
import importlib.util
import logging
import sys
from types import ModuleType
from typing import Dict, List, Optional

from django.urls import path, include

from ..config import OpenAPIConfig
from .detector import GroupDetector

logger = logging.getLogger(__name__)


def _deferred_include(urls_module: str):
    """
    Create a deferred URL include that resolves lazily on first HTTP request.

    When an app's urls.py can't be imported at startup due to circular imports
    (e.g., apps.machines <-> apps.terminal), this wraps it in a lazy object
    that retries the import on first access — by which time all modules are
    fully initialized.
    """
    _resolved = None

    class _LazyUrlconf:
        @property
        def urlpatterns(self):
            nonlocal _resolved
            if _resolved is None:
                try:
                    mod = importlib.import_module(urls_module)
                    _resolved = mod.urlpatterns
                except Exception as e:
                    logger.error(f"Deferred include failed for {urls_module}: {e}")
                    _resolved = []
            return _resolved

    return (_LazyUrlconf(), None, None)


class GroupManager:
    """
    Manages application groups for OpenAPI schema generation.

    Features:
    - App detection with wildcard matching
    - Dynamic URL configuration generation per group
    - Group validation

    Example:
        >>> config = OpenAPIConfig(
        ...     groups={
        ...         "cfg": OpenAPIGroupConfig(
        ...             apps=["django_cfg.*"],
        ...             title="Framework API",
        ...         ),
        ...     },
        ... )
        >>> manager = GroupManager(config, installed_apps)
        >>> groups = manager.get_groups()
        >>> print(groups["cfg"])  # ['django_cfg.admin', 'django_cfg.logging', ...]
    """

    def __init__(
        self,
        config: OpenAPIConfig,
        installed_apps: Optional[List[str]] = None,
        groups: Optional[Dict[str, 'OpenAPIGroupConfig']] = None,
    ):
        """
        Initialize group manager.

        Args:
            config: OpenAPI configuration
            installed_apps: List of installed Django apps (auto-detected if None)
            groups: Override groups (if None, uses config.groups)
        """
        self.config = config
        self._override_groups = groups
        self.detector = GroupDetector(config) if not groups else None

        # Get installed apps
        if installed_apps is None:
            installed_apps = self._get_installed_apps()

        self.installed_apps = installed_apps
        self._groups_cache: Optional[Dict[str, List[str]]] = None

    def _get_installed_apps(self) -> List[str]:
        """
        Get list of installed Django apps.

        Returns:
            List of app names from Django settings

        Raises:
            RuntimeError: If Django is not configured
        """
        try:
            from django.conf import settings

            if not settings.configured:
                raise RuntimeError("Django settings not configured")

            return list(settings.INSTALLED_APPS)

        except ImportError:
            raise RuntimeError("Django is not installed")

    def get_groups(self) -> Dict[str, List[str]]:
        """
        Get detected groups.

        Returns:
            Dictionary mapping group names to app lists

        Example:
            >>> groups = manager.get_groups()
            >>> print(f"Groups: {list(groups.keys())}")
            >>> print(f"CFG apps: {groups['cfg']}")
        """
        if self._groups_cache is None:
            if self._override_groups:
                # Use override groups - manually detect apps for each group
                self._groups_cache = {}
                for group_name, group_config in self._override_groups.items():
                    matched_apps = []
                    for app_pattern in group_config.apps:
                        if '*' in app_pattern or '?' in app_pattern:
                            # Wildcard matching
                            import fnmatch
                            matched_apps.extend([
                                app for app in self.installed_apps
                                if fnmatch.fnmatch(app, app_pattern)
                            ])
                        else:
                            # Exact match
                            if app_pattern in self.installed_apps:
                                matched_apps.append(app_pattern)
                    self._groups_cache[group_name] = matched_apps
            else:
                # Use detector
                self._groups_cache = self.detector.detect_groups(self.installed_apps)

        return self._groups_cache

    def get_group_apps(self, group_name: str) -> List[str]:
        """
        Get apps for specific group.

        Args:
            group_name: Name of the group

        Returns:
            List of app names for the group

        Example:
            >>> apps = manager.get_group_apps("cfg")
            >>> print(f"CFG group has {len(apps)} apps")
        """
        groups = self.get_groups()
        return groups.get(group_name, [])

    def validate_all_groups(self) -> bool:
        """
        Validate that all groups have at least one app.

        Returns:
            True if all groups are valid

        Raises:
            ValueError: If any group has no apps

        Example:
            >>> try:
            ...     manager.validate_all_groups()
            ...     print("All groups valid!")
            ... except ValueError as e:
            ...     print(f"Validation error: {e}")
        """
        validation = self.detector.validate_groups(self.installed_apps)
        invalid_groups = [name for name, valid in validation.items() if not valid]

        if invalid_groups:
            raise ValueError(
                f"Groups with no matched apps: {', '.join(invalid_groups)}"
            )

        logger.info(f"All {len(validation)} groups validated successfully")
        return True

    def get_ungrouped_apps(self) -> List[str]:
        """
        Get apps that don't belong to any group.

        Returns:
            List of ungrouped app names

        Example:
            >>> ungrouped = manager.get_ungrouped_apps()
            >>> if ungrouped:
            ...     print(f"Warning: {len(ungrouped)} apps not in any group")
        """
        return self.detector.get_ungrouped_apps(self.installed_apps)

    def create_urlconf_module(self, group_name: str) -> ModuleType:
        """
        Create dynamic URL configuration module for a group.

        Builds urlpatterns directly in Python (no exec/eval) and wraps them
        in a synthetic module for drf-spectacular schema generation.

        Args:
            group_name: Name of the group

        Returns:
            Dynamic module with urlpatterns attribute
        """
        apps = self.get_group_apps(group_name)

        if not apps:
            raise ValueError(f"Group '{group_name}' has no apps")

        urlpatterns = self._build_urlpatterns(group_name, apps)

        # Wrap in a module object so drf-spectacular can use it as urlconf
        module_name = f"_django_client_urlconf_{group_name}"
        module = ModuleType(module_name)
        module.__file__ = f"<dynamic: {group_name}>"
        module.urlpatterns = urlpatterns
        sys.modules[module_name] = module

        logger.info(
            f"Created dynamic urlconf for group '{group_name}' with {len(apps)} apps"
        )
        return module

    def _build_urlpatterns(self, group_name: str, apps: List[str]) -> list:
        """
        Build URL patterns for a group based on app type.

        Handles three categories:
        - django_cfg.apps.* — framework built-in apps
        - extensions.apps.* / extensions.modules.* — extension apps
        - custom apps — user apps with circular-import-safe deferred include
        """
        # --- django-cfg built-in apps ---
        if all(a.startswith("django_cfg.apps.") for a in apps):
            patterns = []
            for app_name in apps:
                urls_mod = f"{app_name}.urls"
                try:
                    importlib.import_module(urls_mod)
                except (ImportError, ModuleNotFoundError):
                    logger.debug(f"Django-CFG app '{app_name}' has no urls.py - skipping")
                    continue
                module_name = app_name.split('.')[-1]
                patterns.append(path(f"cfg/{module_name}/", include(urls_mod)))
            return patterns

        # --- extensions wildcard (extensions.apps.*) ---
        if any(a in ("extensions.apps.*", "extensions.modules.*") for a in apps):
            from django_cfg.extensions.urls import get_extension_url_patterns
            return list(get_extension_url_patterns())

        # --- single extension ---
        if (
            len(apps) == 1
            and (apps[0].startswith("extensions.apps.") or apps[0].startswith("extensions.modules."))
            and not apps[0].endswith("*")
        ):
            from django_cfg.extensions.urls import discover_url_modules
            app_name = apps[0]
            ext_name = app_name.split(".")[-1]
            ext_type = "app" if "extensions.apps." in app_name else "module"
            patterns = []
            for url_module, suffix, namespace_suffix in discover_url_modules(ext_name, ext_type):
                url_path = f"cfg/{ext_name}/{suffix}/" if suffix else f"cfg/{ext_name}/"
                namespace = f"ext_{ext_name}{namespace_suffix}"
                patterns.append(path(url_path, include(url_module, namespace=namespace)))
            return patterns

        # --- custom apps (with circular-import-safe deferred include) ---
        return self._build_custom_app_urlpatterns(apps)

    def _build_custom_app_urlpatterns(self, apps: List[str]) -> list:
        """
        Build URL patterns for custom user apps.

        Uses find_spec() to check for urls.py without triggering imports,
        then tries eager include(). On circular import, falls back to a
        deferred include that resolves lazily on first HTTP request.
        """
        api_prefix = getattr(self.config, 'api_prefix', '').strip('/')
        patterns = []

        for app_name in apps:
            urls_mod = f"{app_name}.urls"
            try:
                spec = importlib.util.find_spec(urls_mod)
            except (ModuleNotFoundError, ValueError):
                spec = None

            if spec is None:
                logger.debug(f"App '{app_name}' has no urls.py - skipping")
                continue

            app_basename = app_name.split('.')[-1]
            url_path = f"{api_prefix}/{app_basename}/" if api_prefix else f"{app_basename}/"

            try:
                patterns.append(path(url_path, include(urls_mod)))
            except ImportError as e:
                if "circular import" in str(e) or "partially initialized" in str(e):
                    logger.warning(f"Circular import for '{urls_mod}', using deferred include")
                    patterns.append(path(url_path, _deferred_include(urls_mod)))
                else:
                    logger.error(f"Failed to include '{urls_mod}': {e}", exc_info=True)

        return patterns

    def get_urlconf_name(self, group_name: str) -> str:
        """
        Get URL configuration module name for a group.

        Args:
            group_name: Name of the group

        Returns:
            Module name for use in Django settings

        Example:
            >>> urlconf_name = manager.get_urlconf_name("cfg")
            >>> # Use in settings:
            >>> # ROOT_URLCONF = urlconf_name
        """
        return f"_django_client_urlconf_{group_name}"

    def get_statistics(self) -> Dict:
        """
        Get grouping statistics.

        Returns:
            Dictionary with statistics

        Example:
            >>> stats = manager.get_statistics()
            >>> print(f"Total groups: {stats['total_groups']}")
            >>> print(f"Total apps: {stats['total_apps']}")
            >>> print(f"Ungrouped apps: {stats['ungrouped_apps']}")
        """
        groups = self.get_groups()
        ungrouped = self.get_ungrouped_apps()

        total_apps_in_groups = sum(len(apps) for apps in groups.values())

        return {
            "total_groups": len(groups),
            "total_apps": len(self.installed_apps),
            "total_apps_in_groups": total_apps_in_groups,
            "ungrouped_apps": len(ungrouped),
            "groups": {
                name: {
                    "apps": len(apps),
                    "apps_list": apps,
                }
                for name, apps in groups.items()
            },
            "ungrouped_apps_list": ungrouped,
        }


__all__ = [
    "GroupManager",
]
