from django_cfg.modules.django_admin.icons import Icons
from django_cfg.modules.django_unfold.models.navigation import NavigationSection
from django_cfg.modules.django_unfold.navigation.builder import NavBuilder


def build_payments_section() -> NavigationSection:
    return NavigationSection(
        title="Payments",
        separator=True,
        collapsible=True,
        items=[
            NavBuilder.item("Payments", Icons.PAYMENTS, "cfg_payments", "payment"),
            NavBuilder.item("Webhook Events", Icons.WEBHOOK, "cfg_payments", "paymentevent"),
        ],
    )
