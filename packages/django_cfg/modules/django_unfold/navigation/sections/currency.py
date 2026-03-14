from django_cfg.modules.django_admin.icons import Icons
from django_cfg.modules.django_unfold.models.navigation import NavigationSection
from django_cfg.modules.django_unfold.navigation.builder import NavBuilder


def build_currency_section() -> NavigationSection:
    return NavigationSection(
        title="Currency",
        separator=True,
        collapsible=True,
        items=[
            NavBuilder.item("Exchange Rates", Icons.CURRENCY_EXCHANGE, "cfg_currency", "currencyrate"),
            NavBuilder.item("Currencies", Icons.MONETIZATION_ON, "cfg_currency", "currency"),
        ],
    )
