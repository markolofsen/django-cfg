"""
NavBuilder — URL name and NavigationItem helpers for navigation sections.

NavigationItem.link stores a URL name string (e.g. "admin:app_model_changelist").
NavigationItem.resolved_link then converts it to a callable via auto_resolve_url.

NavBuilder methods return URL name strings so they can be stored in NavigationItem.link.

Usage:
    from django_cfg.modules.django_unfold.navigation.builder import NavBuilder
    from django_cfg.modules.django_admin.icons import Icons

    # Build a changelist URL name string
    url_name = NavBuilder.changelist("django_cfg_accounts", "customuser")
    # → "admin:django_cfg_accounts_customuser_changelist"

    # Build a NavigationItem directly
    item = NavBuilder.item("Users", Icons.PEOPLE, "django_cfg_accounts", "customuser")

    # Non-model named URL
    item = NavBuilder.url_item("Overview", Icons.DASHBOARD, "admin:index")

    # Hardcoded path
    item = NavBuilder.direct_item("Dashboard", Icons.MONITOR_HEART, "/cfg/admin/dashboard/grpc/")
"""


class NavBuilder:
    """Static helpers for building navigation URL names and NavigationItems.

    All methods are staticmethods — no instantiation needed.
    Methods that return URL strings return names suitable for NavigationItem.link,
    which auto-resolves them via auto_resolve_url on access.
    """

    @staticmethod
    def changelist(app_label: str, model_name: str) -> str:
        """Return the Django URL name for the admin changelist.

        Args:
            app_label: Django app label (e.g. "django_cfg_monitor")
            model_name: Lowercase model name (e.g. "frontendevent")

        Returns:
            URL name string: "admin:{app_label}_{model_name}_changelist"
        """
        return f"admin:{app_label}_{model_name}_changelist"

    @staticmethod
    def add(app_label: str, model_name: str) -> str:
        """Return the Django URL name for the admin add view.

        Returns:
            URL name string: "admin:{app_label}_{model_name}_add"
        """
        return f"admin:{app_label}_{model_name}_add"

    @staticmethod
    def change(app_label: str, model_name: str) -> str:
        """Return the Django URL name prefix for the admin change view.

        Returns:
            URL name string: "admin:{app_label}_{model_name}_change"
        """
        return f"admin:{app_label}_{model_name}_change"

    @staticmethod
    def item(title: str, icon: str, app_label: str, model_name: str):
        """Create a NavigationItem pointing to the admin changelist.

        Convenience method — eliminates per-item boilerplate in section files.

        Args:
            title: Display title
            icon: Icons.* constant string
            app_label: Django app label (e.g. "django_cfg_accounts")
            model_name: Lowercase model name (e.g. "customuser")

        Returns:
            NavigationItem
        """
        from django_cfg.modules.django_unfold.models.navigation import NavigationItem
        return NavigationItem(
            title=title,
            icon=icon,
            link=NavBuilder.changelist(app_label, model_name),
        )

    @staticmethod
    def url_item(title: str, icon: str, url_name: str):
        """Create a NavigationItem from any named URL.

        Args:
            title: Display title
            icon: Icons.* constant string
            url_name: Django URL name (e.g. "admin:index", "django_cfg_drf_health")

        Returns:
            NavigationItem
        """
        from django_cfg.modules.django_unfold.models.navigation import NavigationItem
        return NavigationItem(title=title, icon=icon, link=url_name)

    @staticmethod
    def direct_item(title: str, icon: str, path: str):
        """Create a NavigationItem with a hardcoded URL path.

        Args:
            title: Display title
            icon: Icons.* constant string
            path: Direct URL path starting with "/" or "http"

        Returns:
            NavigationItem
        """
        from django_cfg.modules.django_unfold.models.navigation import NavigationItem
        return NavigationItem(title=title, icon=icon, link=path)
