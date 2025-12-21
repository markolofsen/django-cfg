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

    Note: Business apps (knowbase, newsletter, agents, payments, support, leads)
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

    # Integration apps
    if base_module.is_centrifugo_enabled():
        enabled_apps.append("django_cfg.apps.integrations.centrifugo")

    if base_module.should_enable_rq():
        enabled_apps.append("django_cfg.apps.integrations.rq")

    if base_module.is_grpc_enabled():
        enabled_apps.append("django_cfg.apps.integrations.grpc")

    if base_module.is_webpush_enabled():
        enabled_apps.append("django_cfg.apps.integrations.webpush")

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
    path('cfg/health/', include('django_cfg.apps.api.health.urls')),
    path('cfg/endpoints/', include('django_cfg.apps.api.endpoints.urls')),
    path('cfg/commands/', include('django_cfg.apps.api.commands.urls')),
    path('cfg/openapi/', include('django_cfg.modules.django_client.urls')),
    path('cfg/dashboard/', include('django_cfg.apps.api.dashboard.urls')),
    path('cfg/admin/', include('django_cfg.apps.system.frontend.urls')),
    path('cfg/accounts/', include('django_cfg.apps.system.accounts.urls')),
    path('cfg/totp/', include('django_cfg.apps.system.totp.urls')),
]

# External Next.js Admin Integration (conditional)
try:
    from django_cfg.core.config import get_current_config
    _config = get_current_config()
    if _config and _config.nextjs_admin:
        urlpatterns.append(path('cfg/nextjs-admin/', include('django_cfg.modules.nextjs_admin.urls')))
except Exception:
    pass

# Business apps (conditional based on config)
base_module = BaseCfgModule()

# Integration apps (conditional based on config)
if base_module.is_centrifugo_enabled():
    urlpatterns.append(path('cfg/centrifugo/', include('django_cfg.apps.integrations.centrifugo.urls')))

if base_module.should_enable_rq():
    urlpatterns.append(path('cfg/rq/', include('django_cfg.apps.integrations.rq.urls')))

if base_module.is_grpc_enabled():
    urlpatterns.append(path('cfg/grpc/', include('django_cfg.apps.integrations.grpc.urls')))

if base_module.is_webpush_enabled():
    urlpatterns.append(path('cfg/webpush/', include('django_cfg.apps.integrations.webpush.urls')))
