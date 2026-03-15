from django_cfg.modules.django_admin.icons import Icons
from django_cfg.modules.django_unfold.models.navigation import NavigationItem, NavigationSection
from django_cfg.modules.django_unfold.navigation.builder import NavBuilder


def build_dashboard_section() -> NavigationSection:
    items = [
        NavBuilder.url_item("Overview", Icons.DASHBOARD, "admin:index"),
        NavBuilder.url_item("Settings", Icons.SETTINGS, "admin:constance_config_changelist"),
        NavBuilder.url_item("Health Check", Icons.HEALTH_AND_SAFETY, "django_cfg_drf_health"),
        NavBuilder.url_item("Endpoints Status", Icons.API, "endpoints_status_drf"),
    ]
    return NavigationSection(title="Dashboard", separator=True, collapsible=True, items=items)
