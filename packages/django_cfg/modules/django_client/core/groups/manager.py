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

        if is_django_cfg_group:
            # For django-cfg apps, use django_cfg.apps.urls which has all the correct URL structure
            # with proper cfg/ prefixes and conditional app registration
            module_code = f'''"""
Dynamic URL configuration for group: {group_name}

Uses django_cfg.apps.urls which includes all enabled cfg apps with correct prefixes.
Auto-generated by django-client GroupManager.
"""

from django_cfg.apps.urls import urlpatterns
'''
        else:
            # For custom apps, generate URL patterns by including each app's URLs
            urlpatterns = []
            from django.apps import apps as django_apps

            for app_name in apps:
                # Try to include app URLs
                try:
                    # Find app config by full name
                    app_config = None
                    for config in django_apps.get_app_configs():
                        if config.name == app_name:
                            app_config = config
                            break

                    if app_config:
                        # Use actual label from AppConfig
                        app_label = app_config.label
                        # Add API prefix from config (e.g., "api/workspaces/" instead of just "workspaces/")
                        api_prefix = getattr(self.config, 'api_prefix', '').strip('/')
                        if api_prefix:
                            url_path = f"{api_prefix}/{app_label}/"
                        else:
                            url_path = f"{app_label}/"
                        urlpatterns.append(f'    path("{url_path}", include("{app_name}.urls")),')
                    else:
                        logger.debug(f"App '{app_name}' not found in installed apps")
                except Exception as e:
                    logger.debug(f"App '{app_name}' skipped: {e}")
                    continue

            # Create module code
            module_code = f'''"""
Dynamic URL configuration for group: {group_name}

Auto-generated by django-client GroupManager.
"""

from django.urls import path, include

urlpatterns = [
{chr(10).join(urlpatterns)}
]
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
