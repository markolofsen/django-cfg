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
    from django_cfg.modules.django_client.core.config import OpenAPIGroupConfig

    return OpenAPIGroupConfig(
        name="cfg",
        apps=get_enabled_cfg_apps(),
        title="Django-CFG API",
        description="Authentication (OTP), Support, Newsletter, Leads, Knowledge Base, AI Agents, Tasks, Payments, Centrifugo, gRPC, Dashboard",
        version="1.0.0",
    )


# Core API endpoints (always enabled)
urlpatterns = [
    path('og/', include('django_cfg.modules.django_ogimage.http.urls')),
    path('cfg/health/', include('django_cfg.apps.api.health.urls')),
    path('cfg/endpoints/', include('django_cfg.apps.api.endpoints.urls')),
    path('cfg/commands/', include('django_cfg.apps.api.commands.urls')),
    path('cfg/openapi/', include('django_cfg.modules.django_client.urls')),
    path('cfg/dashboard/', include('django_cfg.apps.api.dashboard.urls')),
    path('cfg/accounts/', include('django_cfg.apps.system.accounts.urls')),
    path('cfg/totp/', include('django_cfg.apps.system.totp.urls')),
]

# Streamlit Admin Integration (conditional)
try:
    from django_cfg.core.config import get_current_config
    _config = get_current_config()
    if _config and _config.streamlit_admin:
        urlpatterns.append(path('cfg/streamlit/', include('django_cfg.modules.streamlit_admin.urls')))
except Exception:
    pass

# Business apps (conditional based on config)
base_module = BaseCfgModule()

# Integration apps (conditional based on config)
# django_centrifugo has no REST API — replaced by Streamlit dashboard reading D1 directly



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
