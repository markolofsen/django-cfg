from django_cfg.modules.django_admin.icons import Icons
from django_cfg.modules.django_unfold.models.navigation import NavigationSection
from django_cfg.modules.django_unfold.navigation.builder import NavBuilder


def build_monitor_section() -> NavigationSection:
    return NavigationSection(
        title="Monitor",
        separator=True,
        collapsible=True,
        items=[
            NavBuilder.item("Events", Icons.MONITOR_HEART, "django_cfg_monitor", "frontendevent"),
            NavBuilder.item("Sessions", Icons.PEOPLE, "django_cfg_monitor", "anonymoussession"),
            NavBuilder.item("Server Events", Icons.BUG_REPORT, "django_cfg_monitor", "serverevent"),
        ],
    )
