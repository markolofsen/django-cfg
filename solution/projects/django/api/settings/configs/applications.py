"""Which Django apps this project loads.

Split out of ``api/settings/config.py`` — kept in its own module so the app
list can be scanned (and edited) without wading through the rest of the
config.
"""

from __future__ import annotations


def build_project_apps() -> list[str]:
    """The installed-app list, in load order."""
    return [
        "core",
        "apps.profiles",
        "apps.trading",
        "apps.crypto",
        "apps.dashboard",
    ]
