"""
NavigationManager — orchestrates all navigation sections.

Conditional logic lives here; section content lives in sections/.
"""

import importlib
import traceback
from typing import Any, Dict, List

from django_cfg.utils import get_logger
from django_cfg.modules.base import BaseCfgModule

from django_cfg.modules.django_unfold.models.navigation import NavigationSection
from django_cfg.modules.django_unfold.navigation.sections import (
    build_accounts_section,
    build_currency_section,
    build_dashboard_section,
    build_geo_section,
    build_totp_section,
)

logger = get_logger(__name__)


class NavigationManager(BaseCfgModule):
    """Navigation configuration manager for Unfold."""

    def __init__(self, config=None):
        super().__init__()
        self._config = config
        self._config_loaded = config is not None

    @property
    def config(self):
        if not self._config_loaded:
            try:
                self._config = self.get_config()
            except Exception:
                self._config = None
            finally:
                self._config_loaded = True
        return self._config

    def get_navigation_config(self) -> List[Dict[str, Any]]:
        """Build the complete navigation for the Unfold sidebar."""
        sections: List[NavigationSection] = []

        sections.append(build_dashboard_section())

        if self.is_currency_enabled():
            sections.append(build_currency_section())

        if self.is_geo_enabled():
            sections.append(build_geo_section())

        sections.append(build_accounts_section(
            is_github_oauth_enabled=self.is_github_oauth_enabled()
        ))

        if self.is_totp_enabled():
            sections.append(build_totp_section())

        sections.extend(self._get_extension_navigation())

        return [s.to_dict() for s in sections]

    def _get_extension_navigation(self) -> List[NavigationSection]:
        """Load navigation from auto-discovered extensions."""
        from django_cfg.modules.django_admin.icons import Icons
        from django_cfg.modules.django_unfold.models.navigation import NavigationItem

        sections = []
        try:
            extensions = self._get_discovered_extensions()
            for ext in extensions:
                try:
                    if ext.type != "app" or not ext.manifest:
                        continue
                    config_mod = importlib.import_module(f"extensions.apps.{ext.name}.__cfg__")
                    settings_obj = getattr(config_mod, "settings", None)
                    if not settings_obj or not getattr(settings_obj, "enabled", True):
                        continue
                    nav = getattr(settings_obj, "navigation", None)
                    if not nav:
                        continue

                    items = []
                    for nav_item in nav.items:
                        try:
                            link = getattr(nav_item, "resolved_link", None) or nav_item.link
                            if link and link != "#":
                                icon = nav_item.icon if not isinstance(nav_item.icon, str) else getattr(Icons, nav_item.icon, Icons.EXTENSION)
                                items.append(NavigationItem(title=nav_item.title, icon=icon, link=link))
                        except Exception:
                            logger.warning(f"Failed nav item in extension '{ext.name}':\n{traceback.format_exc()}")

                    if items:
                        section_icon = getattr(nav, "icon", None)
                        if section_icon and isinstance(section_icon, str):
                            section_icon = getattr(Icons, section_icon, Icons.EXTENSION)
                        sections.append(NavigationSection(
                            title=nav.title,
                            separator=True,
                            collapsible=getattr(nav, "collapsible", True),
                            items=items,
                        ))
                except Exception:
                    logger.error(f"Extension '{ext.name}' nav failed:\n{traceback.format_exc()}")
        except Exception:
            logger.error(f"Extension nav discovery failed:\n{traceback.format_exc()}")

        return sections


_navigation_manager = None


def get_navigation_manager() -> NavigationManager:
    global _navigation_manager
    if _navigation_manager is None:
        _navigation_manager = NavigationManager()
    return _navigation_manager
