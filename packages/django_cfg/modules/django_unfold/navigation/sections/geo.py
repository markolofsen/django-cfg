from django_cfg.modules.django_admin.icons import Icons
from django_cfg.modules.django_unfold.models.navigation import NavigationSection
from django_cfg.modules.django_unfold.navigation.builder import NavBuilder


def build_geo_section() -> NavigationSection:
    return NavigationSection(
        title="Geo",
        separator=True,
        collapsible=True,
        items=[
            NavBuilder.item("Countries", Icons.PUBLIC, "cfg_geo", "country"),
            NavBuilder.item("States", Icons.MAP, "cfg_geo", "state"),
            NavBuilder.item("Cities", Icons.LOCATION_CITY, "cfg_geo", "city"),
        ],
    )
