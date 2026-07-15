from django_cfg.modules.django_admin.icons import Icons
from django_cfg.modules.django_unfold.models.navigation import NavigationSection
from django_cfg.modules.django_unfold.navigation.builder import NavBuilder


def build_analytics_section() -> NavigationSection:
    return NavigationSection(
        title="Analytics",
        separator=True,
        collapsible=True,
        items=[
            NavBuilder.item("Sites", Icons.PUBLIC, "cfg_analytics", "analyticssite"),
            NavBuilder.item("Sessions", Icons.GROUP, "cfg_analytics", "analyticssession"),
            NavBuilder.item("Events", Icons.ANALYTICS, "cfg_analytics", "analyticsevent"),
        ],
    )
