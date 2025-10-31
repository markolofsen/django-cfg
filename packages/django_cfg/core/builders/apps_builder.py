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
            "django_cfg.apps.dashboard",  # Dashboard API
        ]

        if self.config.enable_frontend:
            apps.append("django_cfg.apps.frontend")

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

        if self.config.centrifugo and self.config.centrifugo.enabled:
            apps.append("django_cfg.apps.centrifugo")

        if self.config.crypto_fields and self.config.crypto_fields.enabled:
            apps.append("django_crypto_fields.apps.AppConfig")

        # Next.js Admin Integration
        if self.config.nextjs_admin:
            apps.append("django_cfg.modules.nextjs_admin")

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
            # No external app needed - ReArq is embedded
            apps.append("django_cfg.apps.tasks")

        # Add django-crontab if enabled
        if hasattr(self.config, "crontab") and self.config.crontab and self.config.crontab.enabled:
            apps.append("django_crontab")

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

        return apps

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
