"""
Django CFG API URLs

Built-in API endpoints for django_cfg functionality.
"""

from django.urls import path, include
from typing import List, Dict
from django.urls import URLPattern


def _register_group_urls(patterns: List[URLPattern], groups: Dict) -> None:
    """
    Auto-register URLs from OpenAPI groups using convention.

    Convention: cfg_{app} → /cfg/{app}/

    Args:
        patterns: URL patterns list to append to
        groups: OpenAPI groups dict
    """
    for group_name in groups.keys():
        # Only django-cfg apps (convention: cfg_*)
        if not group_name.startswith('cfg_'):
            continue

        # Extract app name: cfg_payments → payments
        app_name = group_name[4:]

        # Register main URLs: /cfg/{app}/
        try:
            patterns.append(
                path(f'cfg/{app_name}/', include(f'django_cfg.apps.{app_name}.urls'))
            )
        except ImportError:
            pass  # URL module doesn't exist

        # Register admin URLs: /cfg/{app}/admin/ (if exists)
        try:
            patterns.append(
                path(f'cfg/{app_name}/admin/', include(f'django_cfg.apps.{app_name}.urls_admin'))
            )
        except ImportError:
            pass  # Admin URL module doesn't exist


def _register_apps_fallback(patterns: List[URLPattern]) -> None:
    """
    Fallback: Register apps when OpenAPI is disabled.

    Uses BaseCfgModule checks to determine which apps are enabled.

    Args:
        patterns: URL patterns list to append to
    """
    from django_cfg.modules.base import BaseCfgModule
    base_module = BaseCfgModule()

    # Business logic apps
    if base_module.is_support_enabled():
        patterns.append(path('cfg/support/', include('django_cfg.apps.support.urls')))

    if base_module.is_accounts_enabled():
        patterns.append(path('cfg/accounts/', include('django_cfg.apps.accounts.urls')))

    if base_module.is_newsletter_enabled():
        patterns.append(path('cfg/newsletter/', include('django_cfg.apps.newsletter.urls')))

    if base_module.is_leads_enabled():
        patterns.append(path('cfg/leads/', include('django_cfg.apps.leads.urls')))

    if base_module.is_knowbase_enabled():
        patterns.append(path('cfg/knowbase/', include('django_cfg.apps.knowbase.urls')))

    if base_module.is_agents_enabled():
        patterns.append(path('cfg/agents/', include('django_cfg.apps.agents.urls')))

    if base_module.should_enable_tasks():
        patterns.append(path('cfg/tasks/', include('django_cfg.apps.tasks.urls')))
        patterns.append(path('cfg/tasks/admin/', include('django_cfg.apps.tasks.urls_admin')))

    if base_module.is_payments_enabled():
        patterns.append(path('cfg/payments/', include('django_cfg.apps.payments.urls')))
        patterns.append(path('cfg/payments/admin/', include('django_cfg.apps.payments.urls_admin')))

    # Standalone apps
    if base_module.is_maintenance_enabled():
        patterns.append(
            path('admin/django_cfg_maintenance/', include('django_cfg.apps.maintenance.urls_admin'))
        )

    if base_module.is_rpc_enabled():
        patterns.append(path('rpc/', include('django_cfg.modules.django_ipc_client.dashboard.urls')))
        patterns.append(path('admin/rpc/', include('django_cfg.modules.django_ipc_client.dashboard.urls_admin')))


def get_django_cfg_urlpatterns() -> List[URLPattern]:
    """
    Get Django CFG URL patterns based on OpenAPI groups.

    Returns:
        List of URL patterns for django_cfg
    """
    patterns = [
        # Core APIs (always enabled)
        path('health/', include('django_cfg.apps.api.health.urls')),
        path('endpoints/', include('django_cfg.apps.api.endpoints.urls')),
        path('commands/', include('django_cfg.apps.api.commands.urls')),

        # OpenAPI schemas (if enabled)
        # Provides /openapi/{group}/schema/
        path('openapi/', include('django_cfg.modules.django_client.urls')),
    ]

    try:
        # Auto-register from OpenAPI groups (preferred)
        from django_cfg.modules.django_client.core import get_openapi_service
        service = get_openapi_service()

        if service and service.is_enabled():
            _register_group_urls(patterns, service.get_groups())
        else:
            # Fallback: Use BaseCfgModule when OpenAPI disabled
            _register_apps_fallback(patterns)

    except Exception:
        # Last resort fallback
        _register_apps_fallback(patterns)

    return patterns


# Generate URL patterns dynamically
urlpatterns = get_django_cfg_urlpatterns()
