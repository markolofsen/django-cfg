"""
Streamlit Admin Module.

Provides Python-only admin panel development using Streamlit,
as an alternative to NextJS admin.

Architecture:
- Models: Pydantic v2 data models (dashboard, rq, etc.)
- Services: Business logic with API client injection
- Views: UI components, layouts, and pages
- Registry: Extension system for custom pages

Usage:
    from django_cfg.modules.streamlit_admin import StreamlitAdminConfig

    config = DjangoConfig(
        streamlit_admin=StreamlitAdminConfig(
            app_path="admin_app",
            theme="vercel-dark",
        ),
    )

Extension Usage:
    # In your project's streamlit/extensions.py:
    from django_cfg.modules.streamlit_admin import page_registry
    import streamlit as st

    @page_registry.register("My Page", icon="star", group="Custom")
    def render_my_page():
        st.title("My Custom Page")
"""

# All imports are lazy to avoid circular dependencies
def __getattr__(name: str):
    if name == "StreamlitAdminConfig":
        from .models.config import StreamlitAdminConfig
        return StreamlitAdminConfig
    if name == "page_registry":
        from .core.registry import page_registry
        return page_registry
    if name == "PageRegistry":
        from .core.registry import PageRegistry
        return PageRegistry
    if name == "PageConfig":
        from .core.registry import PageConfig
        return PageConfig
    if name == "MenuGroup":
        from .core.registry import MenuGroup
        return MenuGroup
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    "StreamlitAdminConfig",
    "page_registry",
    "PageRegistry",
    "PageConfig",
    "MenuGroup",
]
