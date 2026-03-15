"""Sidebar navigation component for Streamlit admin."""

import streamlit as st

# Try to import streamlit-antd-components, fallback to native buttons
try:
    import streamlit_antd_components as sac

    HAS_SAC = True
except ImportError:
    HAS_SAC = False

# Lazy import to avoid circular imports - imported inside functions
page_registry = None


def _get_page_registry():
    """Lazy import of page_registry to avoid circular imports."""
    global page_registry
    if page_registry is None:
        from core.registry import page_registry as pr
        page_registry = pr
    return page_registry


def render_sidebar(current_page: str = "Overview") -> str:
    """Render sidebar navigation menu.

    Args:
        current_page: Currently selected page name.

    Returns:
        Selected page name.
    """
    # Load extensions only once per session
    registry = _get_page_registry()
    if not st.session_state.get("_extensions_loaded"):
        registry.load_extensions()
        st.session_state["_extensions_loaded"] = True

    with st.sidebar:
        if HAS_SAC:
            selected = _render_sac_menu()
        else:
            selected = _render_fallback_menu(current_page)

    return selected


def _get_core_menu_items() -> list:
    """Get core menu items (built-in pages)."""
    return [
        sac.MenuItem("Overview", icon="speedometer2"),
        sac.MenuItem(
            "Monitoring",
            icon="graph-up",
            children=[
                sac.MenuItem("System"),
                sac.MenuItem("Charts"),
                sac.MenuItem("Metrics"),
            ],
        ),
        sac.MenuItem(
            "Services",
            icon="server",
            children=[
                sac.MenuItem("Centrifugo"),
                sac.MenuItem("RQ"),
                sac.MenuItem("gRPC"),
            ],
        ),
        sac.MenuItem(
            "Settings",
            icon="gear",
            children=[
                sac.MenuItem("Users"),
                sac.MenuItem("Apps"),
                sac.MenuItem("Config"),
            ],
        ),
    ]


def _get_extension_menu_items() -> list:
    """Get menu items from registered extensions."""
    registry = _get_page_registry()
    items = []

    # Add top-level extension pages
    for page in registry.get_top_level_pages():
        items.append(sac.MenuItem(page.name, icon=page.icon))

    # Add extension groups
    for group in registry.get_groups():
        children = [sac.MenuItem(p.name, icon=p.icon) for p in group.pages]
        if children:
            items.append(sac.MenuItem(group.name, icon=group.icon, children=children))

    return items


def _render_sac_menu() -> str:
    """Render menu using streamlit-antd-components."""
    # Combine core + extension items
    menu_items = _get_core_menu_items()

    # Add extension items (with divider if any exist)
    extension_items = _get_extension_menu_items()
    if extension_items:
        menu_items.append(sac.MenuItem(type="divider"))
        menu_items.extend(extension_items)

    # Get current page from session state
    current = st.session_state.get("current_page", "Overview")

    # Render menu without forcing index - let sac manage its own state
    selected = sac.menu(
        menu_items,
        key="main_menu",
        open_all=False,
        return_index=False,
    )

    # sac.menu returns None when clicking group headers (parent items)
    # Update session state if a valid page is selected
    if selected:
        st.session_state["current_page"] = selected
        return selected

    # Return current page from session state
    return st.session_state.get("current_page", "Overview")


def _render_fallback_menu(current_page: str) -> str:
    """Render simple button-based menu as fallback."""
    # Core pages
    pages = [
        ("Overview", "speedometer2"),
        ("System", "graph-up"),
        ("RQ", "server"),
        ("Users", "people"),
        ("Settings", "gear"),
    ]

    # Add extension pages
    registry = _get_page_registry()
    for page in registry.get_all_pages():
        pages.append((page.name, page.icon))

    selected = current_page
    for name, icon in pages:
        is_active = current_page == name
        if st.button(
            name,
            key=f"nav_{name}",
            icon=f":material/{icon}:",
            use_container_width=True,
            type="primary" if is_active else "secondary",
        ):
            selected = name

    return selected
