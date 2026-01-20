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
            >>> "django_cfg.apps.business.support" in apps
            True
        """
        apps = []

        # Step 1: Add default apps (with special handling for accounts)
        apps.extend(self._get_default_apps())

        # Step 2: Add django-cfg built-in apps
        apps.extend(self._get_django_cfg_apps())

        # Step 3: Add optional apps (tasks, dashboard)
        apps.extend(self._get_optional_apps())

        # Step 4: Add auto-discovered extensions
        apps.extend(self._get_extension_apps())

        # Step 5: Add project-specific apps
        apps.extend(self.config.project_apps)

        # Step 6: Remove duplicates while preserving order
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

        # Add apps one by one, inserting accounts before admin
        for app in DEFAULT_APPS:
            if app == "django.contrib.admin":
                # Insert accounts before admin (for proper migration order)
                # accounts is always enabled - core django-cfg functionality
                apps.append("django_cfg.apps.system.accounts")
                # TOTP 2FA app - always available for security
                apps.append("django_cfg.apps.system.totp")
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
            "django_cfg.modules.django_llm_monitoring",  # LLM balance monitoring
            "django_cfg.modules.django_cleanup",  # Automatic file cleanup
            "django_cfg.apps.api.health",
            "django_cfg.apps.api.commands",
            "django_cfg.apps.api.dashboard",  # Dashboard API
        ]

        if self.config.enable_frontend:
            apps.append("django_cfg.apps.system.frontend")

        # Integrations (enabled via config)
        if self.config.centrifugo and self.config.centrifugo.enabled:
            apps.append("django_cfg.apps.integrations.centrifugo")

        if self.config.grpc and self.config.grpc.enabled:
            apps.append("django_cfg.apps.integrations.grpc")

        if self.config.webpush and self.config.webpush.enabled:
            apps.append("django_cfg.apps.integrations.webpush")

        if self.config.crypto_fields and self.config.crypto_fields.enabled:
            apps.append("django_crypto_fields.apps.AppConfig")

        # Currency app (exchange rates management)
        if self.config.currency and self.config.currency.enabled:
            apps.append("django_cfg.apps.tools.currency")

        # Geo app (countries, states, cities database)
        if self.config.geo and self.config.geo.enabled:
            apps.append("django_cfg.apps.tools.geo")

        # Next.js Admin Integration
        if self.config.nextjs_admin:
            apps.append("django_cfg.modules.nextjs_admin")

        return apps

    def _get_extension_apps(self) -> List[str]:
        """
        Get auto-discovered extension apps from extensions/ folder.

        Extensions are discovered automatically from:
        - extensions/apps/ - Django apps with models
        - extensions/modules/ - Utility modules (not added to INSTALLED_APPS)

        Returns:
            List of extension app labels
        """
        try:
            from django_cfg.extensions import get_extension_loader

            loader = get_extension_loader(base_path=self.config.base_dir)
            return loader.get_installed_apps()
        except Exception as e:
            # Don't fail if extensions module has issues
            from django_cfg.utils import get_logger
            logger = get_logger(__name__)
            logger.debug(f"Extension discovery skipped: {e}")
            return []

    def _get_optional_apps(self) -> List[str]:
        """
        Get optional apps like background tasks, dashboard apps, and frontend integrations.

        Returns:
            List of optional app labels
        """
        apps = []

        # Add Django-RQ if enabled
        if hasattr(self.config, "django_rq") and self.config.django_rq and self.config.django_rq.enabled:
            apps.append("django_rq")  # Core django-rq package
            apps.append("django_cfg.apps.integrations.rq")  # Django-CFG monitoring & API

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
