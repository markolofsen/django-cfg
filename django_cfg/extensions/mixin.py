"""
Extension Mixin for BaseCfgModule

Provides extension-related methods that can be mixed into BaseCfgModule
or used standalone for checking extension status.
"""

from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from .scanner import DiscoveredExtension


class ExtensionMixin:
    """
    Mixin providing extension discovery methods.

    Mix this into BaseCfgModule or use standalone.

    Usage in BaseCfgModule:
        class BaseCfgModule(ExtensionMixin):
            ...

    Usage standalone:
        mixin = ExtensionMixin()
        if mixin.is_extension_enabled("leads"):
            ...
    """

    _extension_cache: Optional[List["DiscoveredExtension"]] = None

    def _get_discovered_extensions(self) -> List["DiscoveredExtension"]:
        """
        Get all discovered extensions (cached).

        Returns:
            List of DiscoveredExtension objects
        """
        if self._extension_cache is not None:
            return self._extension_cache

        try:
            from .loader import get_extension_loader

            # Get config - try get_config method first (BaseCfgModule)
            config = None
            if hasattr(self, "get_config"):
                config = self.get_config()
            elif hasattr(self, "config"):
                config = self.config

            if not config or not hasattr(config, "base_dir"):
                return []

            loader = get_extension_loader(base_path=config.base_dir)
            self._extension_cache = loader.scanner.discover_all()
            return self._extension_cache

        except Exception:
            return []

    def is_extension_enabled(self, name: str) -> bool:
        """
        Check if an extension is enabled (discovered).

        Args:
            name: Extension name to check

        Returns:
            True if extension is discovered, False otherwise

        Example:
            if self.is_extension_enabled("leads"):
                # leads extension is available
        """
        extensions = self._get_discovered_extensions()
        return any(ext.name == name and ext.is_valid for ext in extensions)

    def get_extension(self, name: str) -> Optional["DiscoveredExtension"]:
        """
        Get extension by name.

        Args:
            name: Extension name

        Returns:
            DiscoveredExtension or None if not found
        """
        extensions = self._get_discovered_extensions()
        for ext in extensions:
            if ext.name == name:
                return ext
        return None

    def get_extension_navigation(self) -> List[dict]:
        """
        Get navigation configuration from all extensions.

        Returns list of navigation section dicts ready for Unfold.

        Returns:
            List of navigation section dictionaries
        """
        from django.urls import reverse_lazy

        sections = []

        for ext in self._get_discovered_extensions():
            if not ext.manifest or not ext.manifest.navigation:
                continue

            nav = ext.manifest.navigation
            app_label = ext.manifest.get_django_app_label()

            items = []
            for item in nav.items:
                # Resolve URL
                link = item.link
                if not link and item.model:
                    try:
                        url_name = f"admin:{app_label}_{item.model}_changelist"
                        link = str(reverse_lazy(url_name))
                    except Exception:
                        continue

                if link:
                    items.append({
                        "title": item.title,
                        "icon": item.icon,
                        "link": link,
                    })

            if items:
                sections.append({
                    "title": nav.title,
                    "separator": True,
                    "collapsible": nav.collapsible,
                    "items": items,
                })

        return sections

    def clear_extension_cache(self) -> None:
        """Clear the extension cache to force re-discovery."""
        self._extension_cache = None


# Singleton instance for standalone usage
_extension_helper: Optional[ExtensionMixin] = None


def get_extension_helper() -> ExtensionMixin:
    """Get singleton ExtensionMixin instance."""
    global _extension_helper
    if _extension_helper is None:
        _extension_helper = ExtensionMixin()
    return _extension_helper
