from django_cfg.modules.django_admin.icons import Icons
from django_cfg.modules.django_unfold.models.navigation import NavigationSection
from django_cfg.modules.django_unfold.navigation.builder import NavBuilder


def build_centrifugo_section() -> NavigationSection:
    return NavigationSection(
        title="Centrifugo",
        separator=True,
        collapsible=True,
        items=[
            NavBuilder.direct_item("Dashboard", Icons.MONITOR_HEART, "/cfg/admin/admin/dashboard/centrifugo/"),
            NavBuilder.item("Logs", Icons.LIST_ALT, "django_cfg_centrifugo", "centrifugolog"),
        ],
    )
