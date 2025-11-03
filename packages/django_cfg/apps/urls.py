"""
Django CFG API URLs

Built-in API endpoints for django_cfg functionality.
"""

from typing import List

from django.urls import include, path

from django_cfg.modules.base import BaseCfgModule


def get_enabled_cfg_apps() -> List[str]:
    """
    Get list of enabled django-cfg apps based on configuration.

    Returns:
        List of enabled app paths (e.g., ['django_cfg.apps.business.accounts', ...])
    """
    base_module = BaseCfgModule()
    enabled_apps = []

    if base_module.is_accounts_enabled():
        enabled_apps.append("django_cfg.apps.business.accounts")

    if base_module.is_knowbase_enabled():
        enabled_apps.append("django_cfg.apps.business.knowbase")

    if base_module.is_support_enabled():
        enabled_apps.append("django_cfg.apps.business.support")

    if base_module.is_newsletter_enabled():
        enabled_apps.append("django_cfg.apps.business.newsletter")

    if base_module.is_leads_enabled():
        enabled_apps.append("django_cfg.apps.business.leads")

    if base_module.is_agents_enabled():
        enabled_apps.append("django_cfg.apps.business.agents")

    if base_module.is_payments_enabled():
        enabled_apps.append("django_cfg.apps.business.payments")

    if base_module.is_centrifugo_enabled():
        enabled_apps.append("django_cfg.apps.integrations.centrifugo")

    if base_module.should_enable_rq():
        enabled_apps.append("django_cfg.apps.integrations.rq")

    if base_module.is_grpc_enabled():
        enabled_apps.append("django_cfg.apps.integrations.grpc")

    return enabled_apps


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
    path('cfg/dashboard/', include('django_cfg.apps.system.dashboard.urls')),
    path('cfg/admin/', include('django_cfg.apps.system.frontend.urls')),
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

if base_module.is_accounts_enabled():
    urlpatterns.append(path('cfg/accounts/', include('django_cfg.apps.business.accounts.urls')))

if base_module.is_knowbase_enabled():
    urlpatterns.append(path('cfg/knowbase/', include('django_cfg.apps.business.knowbase.urls')))
    urlpatterns.append(path('cfg/knowbase/system/', include('django_cfg.apps.business.knowbase.urls_system')))
    urlpatterns.append(path('cfg/knowbase/admin/', include('django_cfg.apps.business.knowbase.urls_admin')))

if base_module.is_support_enabled():
    urlpatterns.append(path('cfg/support/', include('django_cfg.apps.business.support.urls')))

if base_module.is_newsletter_enabled():
    urlpatterns.append(path('cfg/newsletter/', include('django_cfg.apps.business.newsletter.urls')))

if base_module.is_leads_enabled():
    urlpatterns.append(path('cfg/leads/', include('django_cfg.apps.business.leads.urls')))

if base_module.is_agents_enabled():
    urlpatterns.append(path('cfg/agents/', include('django_cfg.apps.business.agents.urls')))

if base_module.is_payments_enabled():
    urlpatterns.append(path('cfg/payments/', include('django_cfg.apps.business.payments.urls')))

# Integration apps (conditional based on config)
if base_module.is_centrifugo_enabled():
    urlpatterns.append(path('cfg/centrifugo/', include('django_cfg.apps.integrations.centrifugo.urls')))

if base_module.should_enable_rq():
    urlpatterns.append(path('cfg/rq/', include('django_cfg.apps.integrations.rq.urls')))

if base_module.is_grpc_enabled():
    urlpatterns.append(path('cfg/grpc/', include('django_cfg.apps.integrations.grpc.urls')))
