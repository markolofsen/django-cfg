"""
Third-party integrations registry.
"""

THIRD_PARTY_REGISTRY = {
    # Django Revolution
    "RevolutionConfig": ("django_cfg.models.revolution", "RevolutionConfig"),
    "APIZone": ("django_revolution.config", "ZoneModel"),
    "ZoneModel": ("django_revolution.config", "ZoneModel"),
    "ZoneConfig": ("django_revolution.app_config", "ZoneConfig"),
    "DjangoRevolutionSettings": ("django_revolution.config", "DjangoRevolutionSettings"),
    
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
    "StatCard": ("django_cfg.modules.django_unfold.models.dashboard", "StatCard"),
    "SystemHealthItem": ("django_cfg.modules.django_unfold.models.dashboard", "SystemHealthItem"),
    "QuickAction": ("django_cfg.modules.django_unfold.models.dashboard", "QuickAction"),
    "DashboardWidget": ("django_cfg.modules.django_unfold.models.dashboard", "DashboardWidget"),
    "DashboardData": ("django_cfg.modules.django_unfold.models.dashboard", "DashboardData"),
    "ChartDataset": ("django_cfg.modules.django_unfold.models.dashboard", "ChartDataset"),
    "ChartData": ("django_cfg.modules.django_unfold.models.dashboard", "ChartData"),
    "TabConfiguration": ("django_cfg.modules.django_unfold.models.tabs", "TabConfiguration"),
    "TabItem": ("django_cfg.modules.django_unfold.models.tabs", "TabItem"),
    
    # Django REST Framework
    "DRFConfig": ("django_cfg.models.drf", "DRFConfig"),
    "SpectacularConfig": ("django_cfg.models.drf", "SpectacularConfig"),
    "SwaggerUISettings": ("django_cfg.models.drf", "SwaggerUISettings"),
    "RedocUISettings": ("django_cfg.models.drf", "RedocUISettings"),
    
    # Constance
    "ConstanceConfig": ("django_cfg.models.constance", "ConstanceConfig"),
    "ConstanceField": ("django_cfg.models.constance", "ConstanceField"),
    
    # Ngrok
    "NgrokConfig": ("django_cfg.models.ngrok", "NgrokConfig"),
    "NgrokAuthConfig": ("django_cfg.models.ngrok", "NgrokAuthConfig"),
    "NgrokTunnelConfig": ("django_cfg.models.ngrok", "NgrokTunnelConfig"),
    
    # Material Icons
    "Icons": ("django_cfg.modules.django_unfold.icons", "Icons"),
    "IconCategories": ("django_cfg.modules.django_unfold.icons", "IconCategories"),
}
