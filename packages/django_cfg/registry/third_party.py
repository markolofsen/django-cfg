"""
Third-party integrations registry.
"""

THIRD_PARTY_REGISTRY = {
    # Django Client (OpenAPI)
    "OpenAPIClientConfig": ("django_cfg.models.django.openapi", "OpenAPIClientConfig"),
    "OpenAPIGroupConfig": ("django_cfg.modules.django_client.core.config", "OpenAPIGroupConfig"),
    "OpenAPIConfig": ("django_cfg.modules.django_client.core.config", "OpenAPIConfig"),

    # Unfold Admin
    "UnfoldConfig": ("django_cfg.modules.django_unfold.models.config", "UnfoldConfig"),
    "UnfoldTheme": ("django_cfg.modules.django_unfold.models.config", "UnfoldTheme"),
    "UnfoldThemeConfig": ("django_cfg.modules.django_unfold.models.config", "UnfoldThemeConfig"),
    "UnfoldColors": ("django_cfg.modules.django_unfold.models.config", "UnfoldColors"),
    "UnfoldSidebar": ("django_cfg.modules.django_unfold.models.config", "UnfoldSidebar"),
    "UnfoldDashboardConfig": ("django_cfg.modules.django_unfold.models.config", "UnfoldDashboardConfig"),
    "NavigationItem": ("django_cfg.modules.django_unfold.models.navigation", "NavigationItem"),
    "NavigationSection": ("django_cfg.modules.django_unfold.models.navigation", "NavigationSection"),
    "NavigationItemType": ("django_cfg.modules.django_unfold.models.navigation", "NavigationItemType"),
    "SiteDropdownItem": ("django_cfg.modules.django_unfold.models.dropdown", "SiteDropdownItem"),

    # Django REST Framework
    "DRFConfig": ("django_cfg.models.api.drf", "DRFConfig"),
    "SpectacularConfig": ("django_cfg.models.api.drf", "SpectacularConfig"),
    "SwaggerUISettings": ("django_cfg.models.api.drf", "SwaggerUISettings"),
    "RedocUISettings": ("django_cfg.models.api.drf", "RedocUISettings"),

    # Constance
    "ConstanceConfig": ("django_cfg.models.django.constance", "ConstanceConfig"),
    "ConstanceField": ("django_cfg.models.django.constance", "ConstanceField"),

    # Ngrok
    "NgrokConfig": ("django_cfg.models.ngrok", "NgrokConfig"),
    "NgrokAuthConfig": ("django_cfg.models.ngrok", "NgrokAuthConfig"),
    "NgrokTunnelConfig": ("django_cfg.models.ngrok", "NgrokTunnelConfig"),

    # Material Icons
    "Icons": ("django_cfg.modules.django_admin.icons", "Icons"),
    "IconCategories": ("django_cfg.modules.django_admin.icons", "IconCategories"),
}
