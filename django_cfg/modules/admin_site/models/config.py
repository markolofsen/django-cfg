"""
Admin site configuration: ``DjangoConfig.admin_site = AdminSiteConfig(...)``.

``to_django_settings`` builds the ``CFG_ADMIN_SITE`` settings dict that
``CfgAdminSite`` (``../site.py``) and ``DevAuthForm`` (``../forms/auth.py``)
read: titles, sidebar navigation, site dropdown, login form and dev autofill.
Every field here has an effect; there are no theme or palette fields, the admin
has the stock Django look.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from .dropdown import SiteDropdownItem
from .navigation import NavigationSection

DEV_AUTH_FORM = "django_cfg.modules.admin_site.forms.DevAuthForm"


class AdminSidebar(BaseModel):
    """Sidebar options of the admin site."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    show_all_applications: bool = Field(
        True,
        description="After the navigation sections, list the registered apps whose models no section links to",
    )
    navigation: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Extra sections as raw dicts ({'title', 'items': [{'title', 'icon', 'link'}]}), after `navigation`",
    )


class AdminSiteConfig(BaseModel):
    """Branding, sidebar navigation, site dropdown and login of the django-cfg admin site."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    # Branding
    site_title: Optional[str] = Field(
        default=None,
        description="Browser title of admin pages (default: '<project_name> Admin')",
    )
    site_header: Optional[str] = Field(
        default=None,
        description="Header text (default: project_name)",
    )
    site_subheader: Optional[str] = Field(
        default=None,
        description="Small text next to the header (default: none)",
    )
    site_symbol: str = Field(
        default="settings",
        description="Material Symbols icon name shown before the header",
    )
    site_url: str = Field(
        default="/",
        description="Target of the 'View site' link",
    )

    # Sidebar
    sidebar: AdminSidebar = Field(
        default_factory=AdminSidebar,
        description="Sidebar options",
    )
    navigation: List[NavigationSection] = Field(
        default_factory=list,
        description="Project navigation sections, after the django-cfg ones",
    )

    # User links in the header
    site_dropdown: List[SiteDropdownItem] = Field(
        default_factory=list,
        description="Extra links next to the user links in the header",
    )

    # Login
    login_form: Optional[str] = Field(
        default=None,
        description="Import path of the admin login form (default: stock, or DevAuthForm with dev autofill)",
    )
    dev_autofill_email: Optional[str] = Field(
        default=None,
        description="Email pre-filled on the login form in development",
    )
    dev_autofill_password: Optional[str] = Field(
        default=None,
        description="Password pre-filled on the login form in development",
    )
    dev_autofill_force: bool = Field(
        default=False,
        description="Pre-fill even outside development (ignores the DEBUG check)",
    )

    def to_django_settings(self, project_name: str = "") -> Dict[str, Any]:
        """The ``CFG_ADMIN_SITE`` settings dict. Unset titles come from ``project_name``."""
        site: Dict[str, Any] = {
            "SITE_TITLE": self.site_title or f"{project_name} Admin".strip(),
            "SITE_HEADER": self.site_header or project_name or "Admin",
            "SITE_URL": self.site_url,
            "SITE_SYMBOL": self.site_symbol,
        }
        if self.site_subheader:
            site["SITE_SUBHEADER"] = self.site_subheader

        sidebar = self.sidebar

        def get_navigation(request=None):
            """Built per request: URL names resolve only once Django is ready."""
            nav_items: List[Dict[str, Any]] = []
            try:
                from ..navigation import NavigationManager
                nav_items = NavigationManager().get_navigation_config()
            except Exception:
                pass

            for group in self.navigation:
                group_dict: Dict[str, Any] = {
                    "title": group.title,
                    "separator": group.separator,
                    "collapsible": group.collapsible,
                    "items": [item.to_dict() for item in group.items],
                }
                if group.open:
                    group_dict["open"] = True
                nav_items.append(group_dict)

            nav_items.extend(sidebar.navigation)
            return nav_items

        site["SIDEBAR"] = {
            "show_all_applications": sidebar.show_all_applications,
            "navigation": get_navigation,
        }

        if self.site_dropdown:
            site["SITE_DROPDOWN"] = [item.to_dict() for item in self.site_dropdown]

        if self.dev_autofill_email:
            site["DEV_AUTOFILL_EMAIL"] = self.dev_autofill_email
        if self.dev_autofill_password:
            site["DEV_AUTOFILL_PASSWORD"] = self.dev_autofill_password
        if self.dev_autofill_force:
            site["DEV_AUTOFILL_FORCE"] = self.dev_autofill_force

        login_form = self.login_form
        if not login_form and (self.dev_autofill_email or self.dev_autofill_password):
            login_form = DEV_AUTH_FORM
        if login_form:
            site["LOGIN"] = {"form": login_form}

        return {"CFG_ADMIN_SITE": site}
