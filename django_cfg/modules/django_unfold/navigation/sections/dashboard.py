from django.http import HttpRequest

from django_cfg.modules.django_admin.icons import Icons
from django_cfg.modules.django_unfold.models.navigation import NavigationItem, NavigationSection
from django_cfg.modules.django_unfold.navigation.builder import NavBuilder


def _is_superuser(request: HttpRequest) -> bool:
    return bool(request.user and request.user.is_authenticated and request.user.is_superuser)


def build_dashboard_section() -> NavigationSection:
    items = [
        NavigationItem(title="Overview", icon=Icons.DASHBOARD, link="admin:index", permission=_is_superuser),
        NavigationItem(title="Settings", icon=Icons.SETTINGS, link="admin:constance_config_changelist", permission=_is_superuser),
        NavigationItem(title="Health Check", icon=Icons.HEALTH_AND_SAFETY, link="django_cfg_drf_health", permission=_is_superuser),
        NavigationItem(title="Endpoints Status", icon=Icons.API, link="endpoints_status_drf", permission=_is_superuser),
    ]
    return NavigationSection(title="Dashboard", separator=True, collapsible=True, items=items)
