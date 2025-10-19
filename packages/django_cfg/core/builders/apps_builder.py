"""
INSTALLED_APPS builder for Django-CFG.

Single Responsibility: Build Django INSTALLED_APPS list from configuration.
Extracted from original config.py (903 lines) for better maintainability.

Size: ~220 lines (focused on one task)
"""

from typing import TYPE_CHECKING, List

from ..constants import DEFAULT_APPS

if TYPE_CHECKING:
    from ..base.config_model import DjangoConfig


class InstalledAppsBuilder:
    """
    Builds INSTALLED_APPS list from DjangoConfig.

    Responsibilities:
    - Combine default Django/third-party apps
    - Add django-cfg apps based on enabled features
    - Handle special ordering (accounts before admin)
    - Auto-enable tasks if needed
    - Auto-detect dashboard apps from Unfold
    - Add project-specific apps
    - Remove duplicates while preserving order

    Example:
        ```python
        builder = InstalledAppsBuilder(config)
        apps = builder.build()
        ```
    """

    def __init__(self, config: "DjangoConfig"):
        """
        Initialize builder with configuration.

        Args:
            config: DjangoConfig instance
        """
        self.config = config

    def build(self) -> List[str]:
        """
        Build complete INSTALLED_APPS list.

        Returns:
            List of Django app labels in correct order

        Example:
            >>> config = DjangoConfig(enable_support=True)
            >>> builder = InstalledAppsBuilder(config)
            >>> apps = builder.build()
            >>> "django_cfg.apps.support" in apps
            True
        """
        apps = []

        # Step 1: Add default apps (with special handling for accounts)
        apps.extend(self._get_default_apps())

        # Step 2: Add django-cfg built-in apps
        apps.extend(self._get_django_cfg_apps())

        # Step 3: Add optional apps (tasks, dashboard)
        apps.extend(self._get_optional_apps())

        # Step 4: Add project-specific apps
        apps.extend(self.config.project_apps)

        # Step 5: Remove duplicates while preserving order
        return self._deduplicate(apps)

    def _get_default_apps(self) -> List[str]:
        """
        Get base Django and third-party apps.

        Handles special case: accounts app must be inserted before admin
        for proper migration order.

        Returns:
            List of default app labels
        """
        apps = []

        # Add apps one by one, inserting accounts before admin if enabled
        for app in DEFAULT_APPS:
            if app == "django.contrib.admin":
                # Insert accounts before admin if enabled (for proper migration order)
                if self.config.enable_accounts:
                    apps.append("django_cfg.apps.accounts")
            apps.append(app)

        return apps

    def _get_django_cfg_apps(self) -> List[str]:
        """
        Get django-cfg built-in apps based on enabled features.

        Returns:
            List of django-cfg app labels
        """
        apps = [
            # Core apps (always enabled)
            "django_cfg.modules.django_tailwind",  # Universal Tailwind layouts
            "django_cfg.apps.api.health",
            "django_cfg.apps.api.commands",
        ]

        # Add optional apps based on configuration
        if self.config.enable_support:
            apps.append("django_cfg.apps.support")

        if self.config.enable_newsletter:
            apps.append("django_cfg.apps.newsletter")

        if self.config.enable_leads:
            apps.append("django_cfg.apps.leads")

        if self.config.enable_knowbase:
            apps.append("django_cfg.apps.knowbase")

        if self.config.enable_agents:
            apps.append("django_cfg.apps.agents")

        if self.config.enable_maintenance:
            apps.append("django_cfg.apps.maintenance")

        if self.config.payments and self.config.payments.enabled:
            apps.append("django_cfg.apps.payments")

        if self.config.django_ipc and self.config.django_ipc.enabled:
            apps.append("django_cfg.apps.ipc")

        return apps

    def _get_optional_apps(self) -> List[str]:
        """
        Get optional apps like background tasks, dashboard apps, and frontend integrations.

        Returns:
            List of optional app labels
        """
        apps = []

        # Auto-enable tasks if needed by other features
        if self.config.should_enable_tasks():
            apps.append("django_dramatiq")  # Add django_dramatiq first
            apps.append("django_cfg.apps.tasks")

        # Add DRF Tailwind theme module (uses Tailwind via CDN)
        if self.config.enable_drf_tailwind:
            apps.append("django_cfg.modules.django_drf_theme.apps.DjangoDRFThemeConfig")

        # Add Tailwind CSS apps (optional, only if theme app exists)
        # Note: DRF Tailwind theme doesn't require these
        try:
            import importlib
            importlib.import_module(self.config.tailwind_app_name)
            apps.append("tailwind")
            apps.append(self.config.tailwind_app_name)
        except (ImportError, ModuleNotFoundError):
            # Tailwind app not installed, skip it
            pass

        # Add browser reload in development (if installed)
        if self.config.debug:
            try:
                import django_browser_reload
                apps.append("django_browser_reload")
            except ImportError:
                # django-browser-reload not installed, skip it
                pass

        # Auto-detect dashboard apps from Unfold callback
        dashboard_apps = self._get_dashboard_apps_from_callback()
        apps.extend(dashboard_apps)

        return apps

    def _get_dashboard_apps_from_callback(self) -> List[str]:
        """
        Auto-detect dashboard apps from Unfold dashboard_callback setting.

        Extracts app names from callback paths like:
        - "api.dashboard.callbacks.main_dashboard_callback" → ["api.dashboard"]
        - "myproject.admin.callbacks.dashboard" → ["myproject.admin"]

        This allows django-cfg to automatically add dashboard apps to INSTALLED_APPS
        without requiring manual configuration.

        Returns:
            List of dashboard app names to add to INSTALLED_APPS
        """
        dashboard_apps = []

        # Check if Unfold is configured with a theme
        if not self.config.unfold or not self.config.unfold.theme:
            return dashboard_apps

        # Get dashboard callback path from theme
        callback_path = getattr(self.config.unfold.theme, "dashboard_callback", None)
        if not callback_path:
            return dashboard_apps

        try:
            # Parse callback path: "api.dashboard.callbacks.main_dashboard_callback"
            # Extract app part: "api.dashboard"
            parts = callback_path.split(".")

            # Look for common callback patterns
            callback_indicators = ["callbacks", "views", "handlers"]

            # Find the callback indicator and extract app path before it
            app_parts = []
            for i, part in enumerate(parts):
                if part in callback_indicators:
                    app_parts = parts[:i]  # Everything before the callback indicator
                    break

            # If no callback indicator found, assume last part is function name
            if not app_parts and len(parts) > 1:
                app_parts = parts[:-1]  # Everything except the last part

            if app_parts:
                app_name = ".".join(app_parts)
                dashboard_apps.append(app_name)

        except Exception:
            # If parsing fails, silently continue - dashboard callback is optional
            pass

        return dashboard_apps

    def _deduplicate(self, apps: List[str]) -> List[str]:
        """
        Remove duplicate apps while preserving order.

        Args:
            apps: List of app labels (may contain duplicates)

        Returns:
            Deduplicated list of app labels

        Example:
            >>> builder._deduplicate(["app1", "app2", "app1", "app3"])
            ["app1", "app2", "app3"]
        """
        seen = set()
        return [app for app in apps if not (app in seen or seen.add(app))]


# Export builder
__all__ = ["InstalledAppsBuilder"]
