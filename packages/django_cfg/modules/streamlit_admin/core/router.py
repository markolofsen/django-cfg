"""
Page Router for Streamlit Admin.

Provides a clean way to define and route pages.

Usage:
    router = PageRouter()

    @router.page("Overview", icon="speedometer2")
    def overview_page():
        st.title("Overview")

    @router.page("Settings", icon="gear", group="Admin")
    def settings_page():
        st.title("Settings")

    # In app.py
    router.render(current_page)
"""

from dataclasses import dataclass
from typing import Callable, Optional
import streamlit as st


@dataclass
class RouteConfig:
    """Configuration for a route."""
    name: str
    render_func: Callable[[], None]
    icon: str = "file"
    group: Optional[str] = None
    order: int = 100


class PageRouter:
    """
    Router for Streamlit pages.

    Provides decorator-based page registration and rendering.
    """

    def __init__(self):
        self._routes: dict[str, RouteConfig] = {}
        self._groups: dict[str, list[str]] = {}  # group_name -> [page_names]

    def page(
        self,
        name: str,
        *,
        icon: str = "file",
        group: Optional[str] = None,
        order: int = 100,
    ) -> Callable:
        """
        Decorator to register a page.

        Args:
            name: Page name (shown in menu)
            icon: Material icon name
            group: Group name (None for top-level)
            order: Sort order (lower = higher in menu)

        Example:
            @router.page("Dashboard", icon="speedometer2")
            def dashboard():
                st.title("Dashboard")
        """
        def decorator(func: Callable[[], None]) -> Callable[[], None]:
            route = RouteConfig(
                name=name,
                render_func=func,
                icon=icon,
                group=group,
                order=order,
            )
            self._routes[name] = route

            if group:
                if group not in self._groups:
                    self._groups[group] = []
                self._groups[group].append(name)

            return func
        return decorator

    def register(
        self,
        name: str,
        render_func: Callable[[], None],
        *,
        icon: str = "file",
        group: Optional[str] = None,
        order: int = 100,
    ) -> None:
        """Register a page programmatically."""
        route = RouteConfig(
            name=name,
            render_func=render_func,
            icon=icon,
            group=group,
            order=order,
        )
        self._routes[name] = route

        if group:
            if group not in self._groups:
                self._groups[group] = []
            self._groups[group].append(name)

    def get_route(self, name: str) -> Optional[RouteConfig]:
        """Get route by name."""
        return self._routes.get(name)

    def get_all_routes(self) -> list[RouteConfig]:
        """Get all routes sorted by order."""
        return sorted(self._routes.values(), key=lambda r: (r.order, r.name))

    def get_routes_by_group(self, group: str) -> list[RouteConfig]:
        """Get routes in a specific group."""
        names = self._groups.get(group, [])
        routes = [self._routes[n] for n in names if n in self._routes]
        return sorted(routes, key=lambda r: (r.order, r.name))

    def get_top_level_routes(self) -> list[RouteConfig]:
        """Get routes without a group."""
        routes = [r for r in self._routes.values() if r.group is None]
        return sorted(routes, key=lambda r: (r.order, r.name))

    def get_groups(self) -> list[str]:
        """Get all group names."""
        return list(self._groups.keys())

    def render(self, page_name: str, *, fallback: Optional[Callable[[], None]] = None) -> bool:
        """
        Render a page by name.

        Args:
            page_name: Name of the page to render
            fallback: Optional fallback function if page not found

        Returns:
            True if page was rendered, False otherwise
        """
        route = self.get_route(page_name)
        if route:
            route.render_func()
            return True

        if fallback:
            fallback()
            return True

        return False

    def render_with_fallback(self, page_name: str) -> None:
        """Render page with default fallback for unknown pages."""
        if not self.render(page_name):
            st.title(page_name)
            st.info("Page under construction")
