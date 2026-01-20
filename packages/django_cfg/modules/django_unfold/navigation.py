"""
Default Navigation Configuration for Django CFG Unfold

Provides default navigation sections based on enabled django-cfg modules.
"""

import importlib
import traceback
from typing import Any, Dict, List, Optional

from django.urls import reverse_lazy, NoReverseMatch

from django_cfg.modules.django_admin.icons import Icons
from django_cfg.utils import get_logger
from django_cfg.modules.base import BaseCfgModule

from .models.navigation import NavigationItem, NavigationSection

logger = get_logger(__name__)


class NavigationManager(BaseCfgModule):
    """
    Navigation configuration manager for Unfold.

    Generates default navigation sections based on enabled django-cfg modules.
    """

    def __init__(self, config=None):
        """Initialize navigation manager."""
        super().__init__()
        self._config = config
        self._config_loaded = config is not None

    @property
    def config(self):
        """Lazy load config on first access."""
        if not self._config_loaded:
            try:
                self._config = self.get_config()
            except Exception:
                self._config = None
            finally:
                self._config_loaded = True
        return self._config

    def _safe_reverse(self, url_name: str, fallback: Optional[str] = None) -> Optional[str]:
        """
        Safely resolve URL with error logging.

        Args:
            url_name: Django URL name to reverse
            fallback: Optional fallback URL if reverse fails

        Returns:
            Resolved URL string or fallback, None if both fail
        """
        try:
            return str(reverse_lazy(url_name))
        except NoReverseMatch as e:
            logger.error(
                f"Failed to reverse URL '{url_name}': {e}\n"
                f"Traceback:\n{''.join(traceback.format_tb(e.__traceback__))}"
            )
            if fallback:
                logger.warning(f"Using fallback URL: {fallback}")
                return fallback
            return None
        except Exception as e:
            logger.error(
                f"Unexpected error reversing URL '{url_name}': {e}\n"
                f"Traceback:\n{''.join(traceback.format_exc())}"
            )
            return fallback

    def _create_nav_item(
        self,
        title: str,
        icon: str,
        url_name: str,
        fallback_link: Optional[str] = None
    ) -> Optional[NavigationItem]:
        """
        Create NavigationItem with safe URL resolution.

        Args:
            title: Navigation item title
            icon: Icon identifier
            url_name: Django URL name to reverse
            fallback_link: Optional fallback URL

        Returns:
            NavigationItem or None if URL resolution fails
        """
        link = self._safe_reverse(url_name, fallback_link)
        if link is None:
            logger.warning(f"Skipping navigation item '{title}' - URL '{url_name}' could not be resolved")
            return None

        return NavigationItem(title=title, icon=icon, link=link)

    def _get_extension_navigation(self) -> List[NavigationSection]:
        """
        Get navigation sections from auto-discovered extensions.

        Reads navigation from extension's __cfg__.py -> settings.navigation

        Returns:
            List of NavigationSection for discovered extensions
        """
        sections = []

        try:
            extensions = self._get_discovered_extensions()
            logger.info(f"_get_extension_navigation: found {len(extensions)} extensions")

            for ext in extensions:
                try:
                    logger.debug(f"Processing extension: {ext.name}, type={ext.type}, has_manifest={ext.manifest is not None}")
                    if ext.type != "app" or not ext.manifest:
                        continue

                    # Load navigation from __cfg__.py
                    try:
                        config_mod = importlib.import_module(f"extensions.apps.{ext.name}.__cfg__")
                        nav = getattr(config_mod.settings, "navigation", None)
                    except Exception as e:
                        logger.warning(
                            f"Failed to load navigation for extension '{ext.name}': {e}\n"
                            f"Traceback:\n{traceback.format_exc()}"
                        )
                        continue

                    if not nav:
                        logger.debug(f"Extension '{ext.name}' has no navigation")
                        continue

                    logger.info(f"Loading navigation for extension '{ext.name}': {nav.title} with {len(nav.items)} items")
                    items = []
                    for item in nav.items:
                        try:
                            # Use resolved_link which handles app/model -> URL conversion
                            link = getattr(item, 'resolved_link', None) or item.link
                            if link and link != "#":
                                # icon can be Icons.XXX or string "XXX"
                                icon = item.icon if not isinstance(item.icon, str) else getattr(Icons, item.icon, Icons.EXTENSION)
                                items.append(NavigationItem(title=item.title, icon=icon, link=link))
                        except Exception as e:
                            logger.warning(
                                f"Failed to process navigation item '{getattr(item, 'title', '?')}' for extension '{ext.name}': {e}\n"
                                f"Traceback:\n{traceback.format_exc()}"
                            )

                    if items:
                        # icon can be Icons.XXX or string "XXX" (icon is optional on section)
                        section_icon = getattr(nav, 'icon', None)
                        if section_icon and isinstance(section_icon, str):
                            section_icon = getattr(Icons, section_icon, Icons.EXTENSION)
                        sections.append(NavigationSection(
                            title=nav.title,
                            separator=True,
                            collapsible=getattr(nav, 'collapsible', True),
                            items=items,
                        ))

                except Exception as e:
                    # Catch-all: don't let one broken extension break others
                    logger.error(
                        f"Extension '{ext.name}' navigation failed completely: {e}\n"
                        f"Traceback:\n{traceback.format_exc()}"
                    )

        except Exception as e:
            logger.error(
                f"Failed to load extension navigation: {e}\n"
                f"Traceback:\n{traceback.format_exc()}"
            )

        return sections

    def get_navigation_config(self) -> List[Dict[str, Any]]:
        """Get complete default navigation configuration for Unfold sidebar."""
        # Dashboard section with safe URL resolution
        dashboard_items = []

        # Overview
        overview_item = self._create_nav_item("Overview", Icons.DASHBOARD, "admin:index")
        if overview_item:
            dashboard_items.append(overview_item)

        # Settings
        settings_item = self._create_nav_item("Settings", Icons.SETTINGS, "admin:constance_config_changelist")
        if settings_item:
            dashboard_items.append(settings_item)

        # Health Check
        health_item = self._create_nav_item("Health Check", Icons.HEALTH_AND_SAFETY, "django_cfg_drf_health", "/cfg/health/")
        if health_item:
            dashboard_items.append(health_item)

        # Endpoints Status
        endpoints_item = self._create_nav_item("Endpoints Status", Icons.API, "endpoints_status_drf", "/cfg/endpoints/")
        if endpoints_item:
            dashboard_items.append(endpoints_item)

        navigation_sections = [
            NavigationSection(
                title="Dashboard",
                separator=True,
                collapsible=True,
                items=dashboard_items
            ),
        ]

        # Centrifugo Dashboard (if enabled)
        if self.is_centrifugo_enabled():
            navigation_sections.append(
                NavigationSection(
                    title="Centrifugo",
                    separator=True,
                    collapsible=True,
                    items=[
                        NavigationItem(title="Dashboard", icon=Icons.MONITOR_HEART, link="/cfg/admin/admin/dashboard/centrifugo/"),
                        NavigationItem(title="Logs", icon=Icons.LIST_ALT, link=str(reverse_lazy("admin:django_cfg_centrifugo_centrifugolog_changelist"))),
                    ]
                )
            )

        # gRPC Dashboard (if enabled)
        if self.is_grpc_enabled():
            navigation_sections.append(
                NavigationSection(
                    title="gRPC",
                    separator=True,
                    collapsible=True,
                    items=[
                        NavigationItem(title="Monitor", icon=Icons.MONITOR_HEART, link="/cfg/admin/admin/dashboard/grpc/"),
                        NavigationItem(title="Request Logs", icon=Icons.LIST_ALT, link=str(reverse_lazy("admin:grpc_grpcrequestlog_changelist"))),
                        NavigationItem(title="API Keys", icon=Icons.KEY, link=str(reverse_lazy("admin:grpc_grpcapikey_changelist"))),
                        NavigationItem(title="Server Status", icon=Icons.HEALTH_AND_SAFETY, link=str(reverse_lazy("admin:grpc_grpcserverstatus_changelist"))),
                        NavigationItem(title="Agent Connections", icon=Icons.WIFI, link=str(reverse_lazy("admin:grpc_grpcagentconnectionstate_changelist"))),
                        NavigationItem(title="Connection Events", icon=Icons.TIMELINE, link=str(reverse_lazy("admin:grpc_grpcagentconnectionevent_changelist"))),
                        NavigationItem(title="Connection Metrics", icon=Icons.ANALYTICS, link=str(reverse_lazy("admin:grpc_grpcagentconnectionmetric_changelist"))),
                    ]
                )
            )

        # Web Push (if enabled)
        if self.is_webpush_enabled():
            navigation_sections.append(
                NavigationSection(
                    title="Web Push",
                    separator=True,
                    collapsible=True,
                    items=[
                        NavigationItem(title="Subscriptions", icon=Icons.NOTIFICATIONS, link=str(reverse_lazy("admin:django_cfg_webpush_pushsubscription_changelist"))),
                    ]
                )
            )

        # Currency (if enabled)
        if self.is_currency_enabled():
            navigation_sections.append(
                NavigationSection(
                    title="Currency",
                    separator=True,
                    collapsible=True,
                    items=[
                        NavigationItem(title="Exchange Rates", icon=Icons.CURRENCY_EXCHANGE, link=str(reverse_lazy("admin:cfg_currency_currencyrate_changelist"))),
                        NavigationItem(title="Currencies", icon=Icons.MONETIZATION_ON, link=str(reverse_lazy("admin:cfg_currency_currency_changelist"))),
                    ]
                )
            )

        # Geo (if enabled)
        if self.is_geo_enabled():
            geo_items = []
            countries_item = self._create_nav_item("Countries", Icons.PUBLIC, "admin:cfg_geo_country_changelist")
            if countries_item:
                geo_items.append(countries_item)
            states_item = self._create_nav_item("States", Icons.MAP, "admin:cfg_geo_state_changelist")
            if states_item:
                geo_items.append(states_item)
            cities_item = self._create_nav_item("Cities", Icons.LOCATION_CITY, "admin:cfg_geo_city_changelist")
            if cities_item:
                geo_items.append(cities_item)

            if geo_items:
                navigation_sections.append(
                    NavigationSection(
                        title="Geo",
                        separator=True,
                        collapsible=True,
                        items=geo_items
                    )
                )

        # Add Accounts section
        accounts_items = [
            NavigationItem(title="Users", icon=Icons.PEOPLE, link=str(reverse_lazy("admin:django_cfg_accounts_customuser_changelist"))),
            NavigationItem(title="User Groups", icon=Icons.GROUP, link=str(reverse_lazy("admin:auth_group_changelist"))),
            NavigationItem(title="OTP Secrets", icon=Icons.SECURITY, link=str(reverse_lazy("admin:django_cfg_accounts_otpsecret_changelist"))),
            NavigationItem(title="Registration Sources", icon=Icons.LINK, link=str(reverse_lazy("admin:django_cfg_accounts_registrationsource_changelist"))),
            NavigationItem(title="User Registration Sources", icon=Icons.PERSON, link=str(reverse_lazy("admin:django_cfg_accounts_userregistrationsource_changelist"))),
        ]

        # Add OAuth links if GitHub OAuth is enabled
        if self.is_github_oauth_enabled():
            accounts_items.extend([
                NavigationItem(title="OAuth Connections", icon=Icons.LINK, link=str(reverse_lazy("admin:django_cfg_accounts_oauthconnection_changelist"))),
                NavigationItem(title="OAuth States", icon=Icons.KEY, link=str(reverse_lazy("admin:django_cfg_accounts_oauthstate_changelist"))),
            ])

        navigation_sections.append(NavigationSection(
            title="Users & Access",
            separator=True,
            collapsible=True,
            items=accounts_items
        ))

        if self.is_totp_enabled():
            navigation_sections.append(
                NavigationSection(
                    title="TOTP",
                    separator=True,
                    collapsible=True,
                    items=[
                        NavigationItem(title="TOTP Devices", icon=Icons.PHONE_ANDROID, link=str(reverse_lazy("admin:django_cfg_totp_totpdevice_changelist"))),
                        NavigationItem(title="Backup Codes", icon=Icons.SECURITY, link=str(reverse_lazy("admin:django_cfg_totp_backupcode_changelist"))),
                        NavigationItem(title="2FA Sessions", icon=Icons.VERIFIED_USER, link=str(reverse_lazy("admin:django_cfg_totp_twofactorsession_changelist"))),
                    ]
                )
            )

        # Support section - NOW handled via extensions navigation (see _get_extension_navigation)
        # Newsletter section - NOW handled via extensions navigation (see _get_extension_navigation)
        # Leads section - NOW handled via extensions navigation (see _get_extension_navigation)

        # Agents section - NOW handled via extensions navigation (see _get_extension_navigation)

        # Knowbase section - NOW handled via extensions navigation (see _get_extension_navigation)

        # Payments section - NOW handled via extensions navigation (see _get_extension_navigation)

        # Add auto-discovered extension navigation sections
        extension_sections = self._get_extension_navigation()
        navigation_sections.extend(extension_sections)

        # Convert all NavigationSection objects to dictionaries
        return [section.to_dict() for section in navigation_sections]


# Lazy initialization to avoid circular imports
_navigation_manager = None

def get_navigation_manager() -> NavigationManager:
    """Get the global navigation manager instance."""
    global _navigation_manager
    if _navigation_manager is None:
        _navigation_manager = NavigationManager()
    return _navigation_manager
