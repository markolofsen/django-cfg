"""
Django CFG API URLs

Built-in API endpoints for django_cfg functionality.
"""

from typing import List

from django.urls import include, path

from django_cfg.modules.base import BaseCfgModule


def get_enabled_cfg_apps() -> List[str]:
    """
    Get list of enabled django-cfg built-in apps based on configuration.

    Note: Business apps (knowbase, newsletter, agents, support, leads)
    are now handled via the extensions system (extensions/apps/).
    Use get_extension_apps() for those.

    Returns:
        List of enabled built-in app paths
    """
    base_module = BaseCfgModule()
    enabled_apps = []

    # System apps
    enabled_apps.append("django_cfg.apps.system.accounts")
    enabled_apps.append("django_cfg.apps.system.totp")

    # API apps (always enabled)
    enabled_apps.append("django_cfg.apps.api.dashboard")
    enabled_apps.append("django_cfg.apps.api.health")
    enabled_apps.append("django_cfg.apps.api.commands")

    # Sitemap module — its AppConfig.ready() autoloads per-app sitemap_sources.py
    enabled_apps.append("django_cfg.modules.django_sitemap")

    # Integration apps
    if base_module.is_centrifugo_enabled():
        enabled_apps.append("django_cfg.modules.django_centrifugo")

    if base_module.should_enable_rq():
        enabled_apps.append("django_cfg.modules.django_rq")

    return enabled_apps


def get_extension_apps() -> List[str]:
    """
    Get list of enabled extension apps from extensions/apps/ folder.

    Returns:
        List of extension app paths (e.g., ['extensions.apps.knowbase', ...])
    """
    try:
        from django_cfg.extensions import get_extension_loader
        from django_cfg.core.state import get_current_config

        config = get_current_config()
        if not config:
            return []

        loader = get_extension_loader(base_path=config.base_dir)
        return loader.get_installed_apps()
    except Exception:
        return []


def get_default_cfg_group():
    """
    Returns default OpenAPIGroupConfig for enabled django-cfg apps.
    
    Only includes apps that are enabled in the current configuration.
    
    This can be imported and added to your project's OpenAPIClientConfig groups:
    
    ```python
    from django_cfg.apps.urls import get_default_cfg_group
    
    openapi_client = OpenAPIClientConfig(
        groups=[
            get_default_cfg_group(),
            # ... your custom groups
        ]
    )
    ```
    
    Returns:
        OpenAPIGroupConfig with enabled django-cfg apps
    """
    from django_cfg.modules.django_generator.openapi.pipeline.config import OpenAPIGroupConfig

    return OpenAPIGroupConfig(
        name="cfg",
        apps=get_enabled_cfg_apps(),
        title="Django-CFG API",
        description="Authentication (OTP), Support, Newsletter, Leads, Knowledge Base, AI Agents, Tasks, Centrifugo, gRPC, Dashboard",
        version="1.0.0",
    )


# Core API endpoints (always enabled)
urlpatterns = [
    path('cfg/og/', include('django_cfg.modules.django_ogimage.http.urls')),
    path('cfg/sitemap/', include('django_cfg.modules.django_sitemap.http.urls')),
    path('cfg/health/', include('django_cfg.apps.api.health.urls')),
    path('cfg/endpoints/', include('django_cfg.apps.api.endpoints.urls')),
    path('cfg/commands/', include('django_cfg.apps.api.commands.urls')),
    path('cfg/openapi/', include('django_cfg.modules.django_generator.urls')),
    path('cfg/dashboard/', include('django_cfg.apps.api.dashboard.urls')),
    path('cfg/accounts/', include('django_cfg.apps.system.accounts.urls')),
    path('cfg/totp/', include('django_cfg.apps.system.totp.urls')),
]

# Business apps (conditional based on config)
base_module = BaseCfgModule()

# Integration apps (conditional based on config)
# django_centrifugo: token endpoint for client websocket auth.
# Mounted only when centrifugo is enabled in config.
if base_module.is_centrifugo_enabled():
    urlpatterns.append(
        path('cfg/centrifugo/', include('django_cfg.modules.django_centrifugo.urls'))
    )



# Geo app (countries, states, cities)
if base_module.is_geo_enabled():
    urlpatterns.append(path('cfg/geo/', include('django_cfg.apps.tools.geo.urls')))

# Monitor ingest endpoint — always mounted for OpenAPI visibility.
# POST /cfg/monitor/ingest/ — used by @djangocfg/monitor JS SDK.
# ViewSet returns 503 gracefully if cloudflare is not configured.
# Server-side capture hooks are connected only when cloudflare is ready.
urlpatterns.append(
    path('cfg/monitor/', include('django_cfg.modules.django_monitor.urls'))
)
try:
    from django_cfg.modules.django_cf import is_ready as _cf_ready
    if _cf_ready():
        from django_cfg.modules.django_monitor.capture import connect_capture as _cc
        _cc()
except Exception:
    pass

# MCP endpoint (Model Context Protocol for AI agents)
# Registered unconditionally — module checks enabled state internally
urlpatterns.append(path('cfg/mcp/', include('django_cfg.modules.django_mcp.urls')))

# Custom admin dashboard tabs — always registered; view returns 404 if dashboard not configured
urlpatterns.append(path('cfg/admin/dashboard/', include('django_cfg.modules.django_dashboard.urls')))
