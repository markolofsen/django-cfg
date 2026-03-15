"""Built-in icon registry for OG image branding.

Icons are bundled SVG files located in core/assets/icons/.
They are downloaded by django_admin/icons/generate_icons.py (top-50 by popularity).

Usage::

    from django_cfg.modules.django_ogimage.core.icon import get_icon_path, list_icons

    path = get_icon_path("dashboard")   # Path to dashboard.svg
    names = list_icons()                # ['account_circle', 'dashboard', ...]
"""
from __future__ import annotations

from pathlib import Path

_ICONS_DIR = Path(__file__).parent / "assets" / "icons"


def get_icon_path(name: str) -> Path:
    """Return the absolute path to a bundled SVG icon.

    Raises ValueError if the icon is not found in the built-in set.
    Use list_icons() to see what's available.
    """
    path = _ICONS_DIR / f"{name}.svg"
    if not path.exists():
        available = ", ".join(list_icons()) or "none — run generate_icons.py first"
        raise ValueError(f"Icon {name!r} not found. Available: {available}")
    return path


def list_icons() -> list[str]:
    """Return names of all bundled icons (without .svg extension), sorted."""
    if not _ICONS_DIR.exists():
        return []
    return sorted(p.stem for p in _ICONS_DIR.glob("*.svg"))
