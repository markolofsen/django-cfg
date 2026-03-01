"""
Application Group Manager.

Manages application groups and URL pattern generation.
"""

import logging
import sys
from types import ModuleType
from typing import Dict, List, Optional

from ..config import OpenAPIConfig
from .detector import GroupDetector

logger = logging.getLogger(__name__)


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

        This generates a Python module in memory with URL patterns for all apps
        in the group. The module can be used with drf-spectacular to generate
        OpenAPI schemas for specific app groups.

        Args:
            group_name: Name of the group

        Returns:
            Dynamic module with URL patterns

        Example:
            >>> urlconf = manager.create_urlconf_module("cfg")
            >>> # Use with drf-spectacular:
            >>> # SpectacularAPIView.as_view(urlconf=urlconf)
        """
        apps = self.get_group_apps(group_name)

        if not apps:
            raise ValueError(f"Group '{group_name}' has no apps")

        # Check if this is django-cfg built-in apps group
        is_django_cfg_group = all(
            app_name.startswith("django_cfg.apps.")
            for app_name in apps
        )

        # Check if this is extensions wildcard group (all extensions)
        # Only use get_extension_url_patterns() for wildcard patterns like "extensions.apps.*"
        is_extensions_wildcard = any(
            app_name == "extensions.apps.*" or app_name == "extensions.modules.*"
            for app_name in apps
        )

        # Check if this is a single extension group (e.g., ext_knowbase with just extensions.apps.knowbase)
        is_single_extension = (
            len(apps) == 1 and
            (apps[0].startswith("extensions.apps.") or apps[0].startswith("extensions.modules.")) and
            not apps[0].endswith("*")
        )

        if is_django_cfg_group:
            # For django-cfg apps, generate URL patterns only for apps in this specific group
            # This prevents all groups from getting ALL django-cfg URLs (which causes duplication)
            urlpatterns = []
            for app_name in apps:
                # Extract module name: "django_cfg.apps.system.accounts" -> "accounts"
                parts = app_name.split('.')
                module_name = parts[-1]

                # Check if app has urls.py
                try:
                    import importlib
                    importlib.import_module(f"{app_name}.urls")
                    has_urls = True
                except (ImportError, ModuleNotFoundError):
                    has_urls = False
                    logger.debug(f"Django-CFG app '{app_name}' has no urls.py - skipping")

                if not has_urls:
                    continue

                # Generate URL pattern for this specific app only
                url_path = f'cfg/{module_name}/'
                urlpatterns.append(f'    path("{url_path}", include("{app_name}.urls")),')

            # Create module code
            module_code = f'''"""
Dynamic URL configuration for group: {group_name}

Includes ONLY apps from this specific group (prevents duplication).
Auto-generated by django-client GroupManager.
"""

from django.urls import path, include

urlpatterns = [
{chr(10).join(urlpatterns)}
]
'''
        elif is_extensions_wildcard:
            # For extensions wildcard, use get_extension_url_patterns() which auto-discovers urls*.py
            module_code = f'''"""
Dynamic URL configuration for group: {group_name}

Uses django_cfg.extensions.urls to auto-discover extension URL patterns.
Auto-generated by django-client GroupManager.
"""

from django_cfg.extensions.urls import get_extension_url_patterns

urlpatterns = get_extension_url_patterns()
'''
        elif is_single_extension:
            # For single extension, use discover_url_modules to find all urls*.py
            app_name = apps[0]
            ext_name = app_name.split(".")[-1]  # "knowbase" from "extensions.apps.knowbase"
            ext_type = "app" if "extensions.apps." in app_name else "module"
            module_code = f'''"""
Dynamic URL configuration for group: {group_name}

Single extension: {ext_name}
Auto-discovers all urls*.py files (urls.py, urls_admin.py, urls_system.py, etc.)
Auto-generated by django-client GroupManager.
"""

from django.urls import path, include
from django_cfg.extensions.urls import discover_url_modules

urlpatterns = []

# Discover all urls*.py for this extension
url_modules = discover_url_modules("{ext_name}", "{ext_type}")

for url_module, suffix, namespace_suffix in url_modules:
    if suffix:
        url_path = f"cfg/{ext_name}/{{suffix}}/"
    else:
        url_path = f"cfg/{ext_name}/"

    namespace = f"ext_{ext_name}{{namespace_suffix}}"
    urlpatterns.append(path(url_path, include(url_module, namespace=namespace)))
'''
        else:
            # For custom apps, generate URL patterns by including each app's URLs.
            # NOTE: We use lazy urlpatterns to avoid circular import failures
            # during AppConfig.ready(). Django's include() imports the urls module
            # eagerly, which can fail if apps have cross-app serializer imports
            # (e.g., machines importing from terminal while terminal is not yet loaded).
            url_entries = []

            for app_name in apps:
                try:
                    import importlib.util
                    spec = importlib.util.find_spec(f"{app_name}.urls")
                    if spec is None:
                        logger.debug(f"App '{app_name}' has no urls.py - skipping")
                        continue

                    app_basename = app_name.split('.')[-1]

                    api_prefix = getattr(self.config, 'api_prefix', '').strip('/')
                    if api_prefix:
                        url_path = f"{api_prefix}/{app_basename}/"
                    else:
                        url_path = f"{app_basename}/"

                    url_entries.append((url_path, f"{app_name}.urls"))
                except Exception as e:
                    logger.warning(
                        f"App '{app_name}' skipped: {e}",
                        exc_info=True,
                    )
                    continue

            # Create module with lazy urlpatterns that defer include() calls.
            # The _resolve() function handles circular imports by purging
            # partially-initialized modules from sys.modules and retrying.
            module_code = f'''"""
Dynamic URL configuration for group: {group_name}

Auto-generated by django-client GroupManager.
Urlpatterns are resolved lazily to avoid circular import issues during startup.
"""

import sys
import logging
from django.urls import path, include

_logger = logging.getLogger(__name__)
_url_entries = {url_entries!r}
_resolved = None

def _purge_partial_modules(urls_module_name):
    """Remove partially-initialized modules from sys.modules to allow clean re-import."""
    app_root = urls_module_name.rsplit(".urls", 1)[0]  # e.g. "apps.machines"
    to_remove = []
    for key, mod in sys.modules.items():
        if not key.startswith(app_root):
            continue
        # Detect partially-initialized modules: they exist in sys.modules
        # but their __spec__ may indicate incomplete loading, or they may
        # be missing expected attributes. The safest check: if a module
        # has __spec__ with _initializing=True or has no __file__.
        spec = getattr(mod, "__spec__", None)
        if spec is not None and getattr(spec, "_initializing", False):
            to_remove.append(key)
        elif mod is not None and not hasattr(mod, "__file__"):
            to_remove.append(key)
    for key in to_remove:
        _logger.debug(f"Purging partially-initialized module: {{key}}")
        del sys.modules[key]
    return len(to_remove)

def _resolve():
    global _resolved
    if _resolved is not None:
        return _resolved

    patterns = []
    for url_path, urls_mod in _url_entries:
        try:
            patterns.append(path(url_path, include(urls_mod)))
        except ImportError as e:
            if "circular import" in str(e) or "partially initialized" in str(e):
                _logger.warning(
                    f"Circular import detected for '{{urls_mod}}', "
                    f"purging stale modules and retrying: {{e}}"
                )
                _purge_partial_modules(urls_mod)
                try:
                    patterns.append(path(url_path, include(urls_mod)))
                except Exception as retry_err:
                    _logger.error(
                        f"Failed to include '{{urls_mod}}' after retry: {{retry_err}}",
                        exc_info=True,
                    )
            else:
                _logger.error(f"Failed to include '{{urls_mod}}': {{e}}", exc_info=True)

    _resolved = patterns
    return _resolved

class _LazyUrlpatterns(list):
    """List that resolves URL patterns on first access."""
    def __iter__(self):
        return iter(_resolve())
    def __len__(self):
        return len(_resolve())
    def __getitem__(self, index):
        return _resolve()[index]
    def __bool__(self):
        return bool(_url_entries)

urlpatterns = _LazyUrlpatterns()
'''

        # Create module
        module_name = f"_django_client_urlconf_{group_name}"
        module = ModuleType(module_name)
        module.__file__ = f"<dynamic: {group_name}>"

        # Execute code in module namespace
        exec(module_code, module.__dict__)

        # Add to sys.modules for import resolution
        sys.modules[module_name] = module

        logger.info(
            f"Created dynamic urlconf for group '{group_name}' with {len(apps)} apps"
        )

        return module

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
