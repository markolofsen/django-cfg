"""Django admin (Unfold) — theme, sidebar and the navigation tree.

Split out of ``api/settings/config.py``. It is pure declaration: a menu, some
colours, and the dropdown. Nothing here decides behaviour, so nothing here
needs reading to understand how the project runs — which is exactly what made
it worth moving out of the way.

It imports ``env`` only for the site title.
"""

from __future__ import annotations

from django_cfg import (
    Icons,
    NavigationItem,
    NavigationSection,
    SiteDropdownItem,
    UnfoldColors,
    UnfoldConfig,
    UnfoldSidebar,
)

from api.environment import env


def build_unfold_config() -> UnfoldConfig:
    """The admin interface configuration."""
    return UnfoldConfig(
        dev_autofill_email="admin@example.com",
        dev_autofill_password="admin123",
        site_title=f"{env.app.name} Admin",
        site_header=env.app.name,
        site_subheader="Main Project",
        site_url="/",
        site_symbol=Icons.ROCKET_LAUNCH,
        theme="dark",
        colors=UnfoldColors(primary="#3b82f6"),
        sidebar=UnfoldSidebar(
            show_search=True,
            show_all_applications=True,
        ),
        site_dropdown=[
            SiteDropdownItem(
                icon=Icons.DEVELOPER_BOARD,
                title="Developer",
                link="https://djangocfg.com",
            ),
        ],
        # django-cfg contributes its own sections (Currency, Analytics, TOTP, ...)
        # automatically. Sections for THIS project's apps belong here — they are
        # not auto-discovered, which is why Crypto was missing from the sidebar
        # even though its admin was registered.
        navigation=[
            NavigationSection(
                title="Crypto",
                separator=True,
                collapsible=True,
                items=[
                    NavigationItem(title="Coin Listings", icon=Icons.CURRENCY_BITCOIN, link="admin:crypto_coinlisting_changelist"),
                ],
            ),
            NavigationSection(
                title="Profiles",
                separator=True,
                collapsible=True,
                items=[
                    NavigationItem(title="User Profiles", icon=Icons.PERSON, link="admin:profiles_userprofile_changelist"),
                ],
            ),
        ],
    )
