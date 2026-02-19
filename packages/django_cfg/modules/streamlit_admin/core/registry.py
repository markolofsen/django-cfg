"""
Page and menu registry for Streamlit Admin extensions.

Allows projects to register custom pages that integrate with the base admin.

Usage in project's streamlit/extensions.py:
    from django_cfg.modules.streamlit_admin import page_registry

    @page_registry.register("My Page", icon="star", group="Custom")
    def render_my_page():
        st.title("My Custom Page")
        st.write("Hello from extension!")

    # Or register a class-based page
    page_registry.register_page(
        name="Analytics",
        icon="bar-chart",
        group="Reports",
        render_func=render_analytics,
    )
"""

from dataclasses import dataclass, field
from typing import Callable, Optional
import logging

logger = logging.getLogger("django_cfg.streamlit_admin.registry")


@dataclass
class PageConfig:
    """Configuration for a registered page."""

    name: str
    render_func: Callable[[], None]
    icon: str = "file"
    group: Optional[str] = None  # None = top-level, otherwise grouped under this name
    order: int = 100  # Lower = higher in menu


@dataclass
class MenuGroup:
    """A group of pages in the sidebar menu."""

    name: str
    icon: str = "folder"
    order: int = 100
    pages: list[PageConfig] = field(default_factory=list)


class PageRegistry:
    """
    Registry for Streamlit admin pages.

    Singleton pattern - use `page_registry` instance.
    """

    _instance: Optional["PageRegistry"] = None

    def __new__(cls) -> "PageRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._pages: dict[str, PageConfig] = {}
            cls._instance._groups: dict[str, MenuGroup] = {}
            cls._instance._initialized = False
        return cls._instance

    def register(
        self,
        name: str,
        *,
        icon: str = "file",
        group: Optional[str] = None,
        order: int = 100,
    ) -> Callable:
        """
        Decorator to register a page render function.

        Args:
            name: Page name (shown in menu)
            icon: Icon name (material icons)
            group: Group name (None for top-level)
            order: Sort order (lower = higher)

        Example:
            @page_registry.register("My Page", icon="star", group="Custom")
            def render_my_page():
                st.title("My Page")
        """
        def decorator(func: Callable[[], None]) -> Callable[[], None]:
            self.register_page(
                name=name,
                render_func=func,
                icon=icon,
                group=group,
                order=order,
            )
            return func
        return decorator

    def register_page(
        self,
        name: str,
        render_func: Callable[[], None],
        *,
        icon: str = "file",
        group: Optional[str] = None,
        order: int = 100,
    ) -> None:
        """
        Register a page programmatically.

        Args:
            name: Page name
            render_func: Function that renders the page
            icon: Icon name
            group: Group name (None for top-level)
            order: Sort order
        """
        page = PageConfig(
            name=name,
            render_func=render_func,
            icon=icon,
            group=group,
            order=order,
        )
        self._pages[name] = page

        # Add to group if specified
        if group:
            if group not in self._groups:
                self._groups[group] = MenuGroup(name=group)
            self._groups[group].pages.append(page)

        logger.debug(f"Registered page: {name} (group={group})")

    def register_group(
        self,
        name: str,
        *,
        icon: str = "folder",
        order: int = 100,
    ) -> None:
        """
        Register a menu group.

        Args:
            name: Group name
            icon: Icon name
            order: Sort order
        """
        if name not in self._groups:
            self._groups[name] = MenuGroup(name=name, icon=icon, order=order)
        else:
            self._groups[name].icon = icon
            self._groups[name].order = order

    def get_page(self, name: str) -> Optional[PageConfig]:
        """Get a page by name."""
        return self._pages.get(name)

    def get_all_pages(self) -> list[PageConfig]:
        """Get all registered pages sorted by order."""
        return sorted(self._pages.values(), key=lambda p: (p.order, p.name))

    def get_top_level_pages(self) -> list[PageConfig]:
        """Get pages without a group."""
        return sorted(
            [p for p in self._pages.values() if p.group is None],
            key=lambda p: (p.order, p.name)
        )

    def get_groups(self) -> list[MenuGroup]:
        """Get all groups sorted by order."""
        groups = sorted(self._groups.values(), key=lambda g: (g.order, g.name))
        # Sort pages within each group
        for group in groups:
            group.pages = sorted(group.pages, key=lambda p: (p.order, p.name))
        return groups

    def render_page(self, name: str) -> bool:
        """
        Render a page by name.

        Returns:
            True if page was found and rendered, False otherwise.
        """
        page = self.get_page(name)
        if page:
            page.render_func()
            return True
        return False

    def clear(self) -> None:
        """Clear all registrations (useful for testing)."""
        self._pages.clear()
        self._groups.clear()
        self._initialized = False

    def load_extensions(self, extensions_path: Optional[str] = None) -> None:
        """
        Load page extensions from project's streamlit directory.

        Looks for:
        - {app_path}/extensions.py
        - {app_path}/pages/*.py

        Args:
            extensions_path: Direct path to extensions directory.
                           If None, tries to get from Django config.
        """
        if self._initialized:
            return

        from pathlib import Path
        import importlib.util
        import os

        app_path: Optional[Path] = None

        # 1. Try direct path argument
        if extensions_path:
            app_path = Path(extensions_path)

        # 2. Try environment variable (set by autostart)
        if not app_path:
            env_path = os.environ.get("STREAMLIT_EXTENSIONS_PATH")
            if env_path:
                app_path = Path(env_path)

        # 3. Fallback: look in current working directory
        if not app_path:
            cwd = Path.cwd()
            # Check common locations
            for candidate in ["streamlit", "admin_app", "."]:
                check_path = cwd / candidate
                if (check_path / "extensions.py").exists():
                    app_path = check_path
                    break

        if not app_path or not app_path.exists():
            logger.debug(f"Extension path not found: {app_path}")
            self._initialized = True
            return

        try:
            # Load extensions.py if exists
            extensions_file = app_path / "extensions.py"
            if extensions_file.exists():
                logger.info(f"Loading extensions from: {extensions_file}")
                spec = importlib.util.spec_from_file_location(
                    "streamlit_extensions",
                    extensions_file
                )
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

            # Load pages/*.py files
            pages_dir = app_path / "pages"
            if pages_dir.exists():
                for page_file in sorted(pages_dir.glob("*.py")):
                    if page_file.name.startswith("_"):
                        continue
                    logger.debug(f"Loading page: {page_file}")
                    spec = importlib.util.spec_from_file_location(
                        f"streamlit_page_{page_file.stem}",
                        page_file
                    )
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)

            self._initialized = True
            logger.info(
                f"Loaded {len(self._pages)} extension pages, "
                f"{len(self._groups)} groups"
            )

        except Exception as e:
            logger.warning(f"Failed to load extensions: {e}")
            self._initialized = True


# Singleton instance
page_registry = PageRegistry()
